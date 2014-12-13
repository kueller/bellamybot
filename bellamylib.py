import socket
import filehandle

# Class for parsing the IRC incoming messages.
# Not every message will be associated with every variable
class IRCMessage:
    nick = None
    msgtype = None
    chan = None
    msg = None
    command = None
    argument = None

    def __init__(self, text):
        self.nick = text.split('!')[0].replace(':','')
        self.msgtype = text.split(' ')[1]

        if len(text.split(' ')) >= 3:
            self.chan = text.split(' ')[2]

        if len(text.split(':')) >= 3:
            self.msg = text.split(':')[2]

        if self.msg != None:
            self.command = self.msg.split(' ')[0]

        if self.msg != None and len(self.msg.partition(' ')) >= 3:
            self.argument = self.msg.partition(' ')[2]

# General class for the IRC connection. Contains all join and messaging commands
class BotConnection:
    channel = None
    chat = None
    nick = None

    def __init__(self):
        self.chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, server):
        self.chat.connect((server, 6667))
        self.chat.settimeout(1)

    def setuser(self, name, message):
        self.chat.send(("USER %s botnick botnick :%s\r\n" 
                        % (name, message)).encode('utf-8'))
    def setnick(self, nick):
        self.nick = nick
        self.chat.send(("NICK %s\r\n" % nick).encode('utf-8'))
    def identify(self, password):
        self.chat.send(("PRIVMSG nickserv :identify %s\r\n" 
                        % password).encode('utf-8'))
    def join(self, channel):
        self.channel = channel
        self.chat.send(("JOIN %s\r\n" % self.channel).encode('utf-8'))

    def incoming(self):
        text = self.chat.recv(2048).decode('utf-8')
        print(text)

        if text.find("PING") != -1:
            self.chat.send(("PONG %s\r\n" % (text.split()[1])).encode('utf-8'))

        return IRCMessage(text)

    def msg(self, message):
        self.chat.send(("PRIVMSG %s :%s\r\n" 
                        % (self.channel, message)).encode('utf-8'))
    def kick(self, nick,  message):
        self.chat.send(("KICK %s %s :%s\r\n" 
                        % (self.channel, nick, message)).encode('utf-8'))
    def quitirc(self, message):
        self.chat.send(("QUIT :Quit %s\r\n" % message).encode('utf-8'))
    def memo(self, nick, message):
        self.chat.send(("PRIVMSG memoserv :send %s %s\r\n" 
                        % (nick, message)).encode('utf-8'))

# General needed information about the bot's state and other small strings
# This is where the data from the config file goes
class BotInfo:
    server = None
    channel = None
    nick = None
    password = None
    
    mbid = None

    sourceCode = None

    owner = []
    ops = []

    joinmsg = None
    
    green = False
    greenNick = None

    state = None

    def __init__(self):
        self.owner = []
        self.ops = []
        self.mbid = "9c9f1380-2516-4fc9-a3e6-f9f61941d090"
        self.sourceCode = "http://waa.ai/4m8N"
        self.joinmsg = False
        self.state = False

    def parseConfig(self, filename):
        try:
            configLines = filehandle.get_list(filename)
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
            elif arg == "owner":
                owners = value.split(",")
                for owner in owners:
                    self.owner.append(owner)
            elif arg == "ops":
                ops = value.split(",")
                for op in ops:
                    self.ops.append(op)
            elif arg == "joinmsg":
                if value == "on":
                    self.joinmsg = True
                elif value == "off":
                    self.joinmsg = False
            elif arg == "state":
                if value == "on":
                    self.state = True
                elif value == "off":
                    self.state = False
                        
    def verifyConfig(self):
        if self.server == None or self.nick == None or self.channel == None:
            raise Exception("Server, nick, and channel required in config.")
        if len(self.ops) == 0:
            print("Warning: No channel ops specified.")
        if len(self.owner) == 0:
            print("Warning: No channel owner specified.")    
        if self.password == None:
            print("Warning: No password entered.")
