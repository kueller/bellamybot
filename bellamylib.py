'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
The main library for running the IRC bot. The IRCBot class will be the bot
itself. The settings are run from the config file stored in text/config
(relative to the current folder). The included config contains more details
about its formatting. A simple usage of the IRCBot class would be

   myBot = IRCBot()
   myBot.start()

From there the bot will read the configuration from the config file and
do all the connections.

Use incoming() to receive text which will return an IRCMessage instance.

msg(), quitirc(), memo(), and kick() are also usable methods after join.
Note: Depends on filehandle.py.

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import time
import socket
from filehandle import get_list
from filehandle import remove_nr

# Class for parsing the IRC incoming messages.
# Not every message will be associated with every variable
class IRCMessage:
    nick     = None       # Nick of the user that sent the message.
    msgtype  = None       # The command part of the message.
    chan     = None       # Channel the message is sent to.
    msg      = None       # The full parameters of the command.

    # Meant for use in channel PRIVMSG to handle bot commands.
    command  = None       # The first word in the parameters
    argument = None       # All following words (if any). A single string.

    def __init__(self, text):
        self.nick = text.split('!')[0].replace(':','')

        if len(text.split(' ')) >= 2:
            self.msgtype = text.split(' ')[1]

        if len(text.split(' ')) >= 3:
            self.chan = text.split(' ')[2]

        if len(text.split(':')) >= 3:
            self.msg = text.split(':')[2]

        if self.msg != None:
            self.command = self.msg.split(' ')[0]
        else:
            self.argument = text.split(' ')[len(text.split(' ')) - 1]

        if self.msg != None and len(self.msg.partition(' ')) >= 3:
            self.argument = self.msg.partition(' ')[2]

# General needed information about the bot's state and other small strings
# This is where the data from the config file goes
# An instance of BotInfo is made inside the IRCBot class. There is no need
# to make one separately.
class BotInfo:
    server     = None
    channel    = None
    nick       = None
    password   = None
    
    mbid       = None
    sourceCode = None

    joinmsg    = None
    
    green      = False
    greenNick  = None

    version    = None

    games      = None
    state      = None

    def __init__(self):
        self.mbid = "9c9f1380-2516-4fc9-a3e6-f9f61941d090"
        self.sourceCode = "http://waa.ai/4m8N"
        self.version = "4.1.3"
        self.joinmsg = False
        self.games   = True
        self.state   = False

    def parseConfig(self, filename):
        try:
            configLines = get_list(filename)
        except IOError as e:
            raise IOError(e)

        for line in configLines:
            if line.startswith("#"):
                continue
            splitLine = line.split("=")
            if len(splitLine) < 2:
                continue
            
            arg = splitLine[0].strip()
            value = splitLine[1].strip()

            if arg == "server":
                self.server = value
            elif arg == "channel":
                self.channel = value
            elif arg == "nick":
                self.nick = value
            elif arg == "password":
                self.password = value
            elif arg == "mbid":
                self.mbid = value
            elif arg == "source":
                self.sourceCode = value
            elif arg == "joinmsg":
                if value == "on":
                    self.joinmsg = True
                elif value == "off":
                    self.joinmsg = False
            elif arg == "gamemode":
                if value == "on":
                    self.games = True
                elif value == "off":
                    self.games = False
            elif arg == "state":
                if value == "on":
                    self.state = True
                elif value == "off":
                    self.state = False
                        
    def verifyConfig(self):
        if self.server == None or self.nick == None or self.channel == None:
            raise Exception("Server, nick, and channel required in config.")
        if self.password == None:
            print("Warning: No password entered.")

            
# General class for the IRC connection. Contains all join and messaging commands
class IRCBot:
    chat = None      # Socket connection.
    info = None      # BotInfo instance.

    userlist = []    # All the users in the channel.
    modlist  = []    # All the elevated users, hop and higher.
    owners   = []    # All the owners (will typically be just one if any).

    def __init__(self):
        self.chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info = BotInfo()
        self.info.parseConfig('config')
        self.info.verifyConfig()

    def start(self):
        print("Connecting to %s." % self.info.server)
        
        self.connect(self.info.server)
        self.setuser(self.info.nick, "Hello")
        self.setnick(self.info.nick)
        self.identify(self.info.password)

        print("Bot nick set as %s." % self.info.nick)
        print("Joining channel %s." % self.info.channel)

        self.join(self.info.channel)
        time.sleep(5)

        # 5 second wait ensures call to NAMES will be on its own line.
        self.chat.send(("NAMES %s\r\n" % self.info.channel).encode('utf-8'))
        
    def connect(self, server):
        self.chat.connect((server, 6667))
        self.chat.settimeout(1)

    def setuser(self, name, message):
        self.chat.send(("USER %s botnick botnick :%s\r\n" % (name, message)).encode('utf-8'))
    def setnick(self, nick):
        self.chat.send(("NICK %s\r\n" % nick).encode('utf-8'))
    def identify(self, password):
        self.chat.send(("PRIVMSG nickserv :identify %s\r\n" % password).encode('utf-8'))
    def join(self, channel):
        self.chat.send(("JOIN %s\r\n" % channel).encode('utf-8'))

    def getText(self):
        return self.chat.recv(2048).decode('utf-8')

    # Formats and prepares an IRCMessage instance to return.
    # Also updates the userlists if applicable.
    def incoming(self):
        text = self.getText()
        print(text)
        
        if text.find("PING") != -1:
            self.chat.send(("PONG %s\r\n" % (text.split()[1])).encode('utf-8'))

        message = IRCMessage(text)

        if message.msgtype == "JOIN":
            self.userlist.append(message.nick)
        elif message.msgtype in ("PART", "QUIT"):
            self.userlist.remove(message.nick)
        elif message.msgtype == "KICK":
            self.userlist.remove(text.split(' ')[3])
        elif message.msgtype == "353":
            self.setUserList(text)
        elif message.msgtype == "NICK":
            self.userlist[self.userlist.index(message.nick)] = remove_nr(message.command)
        elif message.msgtype == "MODE":
            if (text.split(' ')[3].startswith("+o") or
                text.split(' ')[3].startswith("+a") or
                text.split(' ')[3].startswith("+h")):
                self.modlist.append(remove_nr(text.split(' ')[4]))
            elif text.split(' ')[3].startswith("+q"):
                self.modlist.append(remove_nr(text.split(' ')[4]))
                self.owners.append(remove_nr(text.split(' ')[4]))
            elif (text.split(' ')[3].startswith("-o") or
                text.split(' ')[3].startswith("-a") or
                text.split(' ')[3].startswith("-h")):
                self.modlist.remove(remove_nr(text.split(' ')[4]))
            elif text.split(' ')[3].startswith("-q"):
                self.modlist.remove(remove_nr(text.split(' ')[4]))
                self.owners.remove(remove_nr(text.split(' ')[4]))

                
        return message

    def msg(self, message):
        self.chat.send(("PRIVMSG %s :%s\r\n" % (self.info.channel, message)).encode('utf-8'))
    def kick(self, nick,  message):
        self.chat.send(("KICK %s %s :%s\r\n" % (self.info.channel, nick, message)).encode('utf-8'))
    def quitirc(self, message):
        self.chat.send(("QUIT :Quit %s\r\n" % message).encode('utf-8'))
    def memo(self, nick, message):
        self.chat.send(("PRIVMSG memoserv :send %s %s\r\n" 
                        % (nick, message)).encode('utf-8'))

    def setUserList(self, text):
        if len(text.split(' ')) < 6:
            return
        if text.split(' ')[1] != "353":
            return

        print("Generating user list...")
        names = text.split(":")[2].split(' ')
        
        for name in names:
            if name[0] in ('%', '@', '&'):
                self.modlist.append(remove_nr(name[1:]))
                self.userlist.append(remove_nr(name[1:]))
            elif name[0] == '~':
                self.modlist.append(remove_nr(name[1:]))
                self.owners.append(remove_nr(name[1:]))
                self.userlist.append(remove_nr(name[1:]))
            else:
                self.userlist.append(remove_nr(name))
