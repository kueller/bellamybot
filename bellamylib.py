'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
The main library for running the IRC bot. The IRCBot class will be the bot
itself. The settings can be done manually or read from a config file. The
example config file shows some of the options. A simple implementation
of the bot would be:

   myBot = IRCBot()
   myBot.setInfoFromConfig('config')
   myBot.start()

From there the bot will read the configuration from the config file and
do all the connections.

Use incoming() to receive text which will return an IRCMessage instance.

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import time
import socket
import random
import threading

# Class for parsing the IRC incoming messages.
# Not every message will be associated with every variable
class IRCMessage:
    message   = ''
    prefix    = ''

    nick      = ''
    host      = ''
    serv      = ''
    
    IRCcmd    = ''
    IRCparams = []
    body      = ''

    command   = ''
    argument  = ''

    def __init__(self, text):
        if text.startswith(':'):
            if len(text.split(' ')) < 2:
                return
            
            self.message = text.partition(':')[2]
            self.prefix  = self.message.split()[0]

            if self.prefix.find('!') != -1 and self.prefix.find('@') != -1:
                self.nick = self.prefix.split('!')[0]
                self.host = self.prefix.split('!')[1].split('@')[0]
                self.serv = self.prefix.split('!')[1].split('@')[0]

            self.IRCcmd = self.message.split()[1]
            
            self.IRCparams = []
            for token in self.message.split(' ')[2:]:
                if token.startswith(':'):
                    break
                self.IRCparams.append(token)

            if len(text.split(':')) > 2:
                self.body     = ':'.join(text.split(':')[2:])
                self.command  = self.body.split(' ')[0]
                if len(self.body.split(' ')) > 1:
                    self.argument = self.body.partition(' ')[2]

# General needed information about the bot's state and other small strings
# This is where the data from the config file goes
# An instance of BotInfo is made inside the IRCBot class. There is no need
# to make one separately.
class _BotInfo:
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
        self.version = "5.2.0"
        self.joinmsg = False
        self.games   = True
        self.state   = False

    def parseConfig(self, filename):
        try:
            with open(filename, 'r') as f:
                configLines = f.read().splitlines()
                configLines = list(configLines)
        except IOError:
            raise IOError("Error opening " + filename)

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

# A timer that stores a time delay (minutes or seconds) that can be checked
# until the localtime has surpassed the delay. Limits are the next highest time
# division (i.e. 1 minute or 1 hour).
class _Timer:
    rawDelay  = None # The amount of time delayed after an initialization
    timeDelay = None # The second or minute on the clock calculated from rawDelay
    timerType = None # "sec" or "min"

    random = False
    randRange = ()

    loop = False

    active = False

    def __init__(self, ttype, delay, rand=False, rrange=(), loop=False):
        self.rawDelay = delay
        if ttype is not "sec" and ttype is not "min":
            raise ValueError("type needs to be \"sec\" or \"min\"")
        self.timerType = ttype
        self.random = rand
        self.randRange = rrange
        self.loop = loop
        self.__setDelay(self.rawDelay)
        self.active = True

    # If the loop is a randomly generated range, the raw delay is ignored.
    def __setDelay(self, delay):
        if self.random:
            if len(self.randRange) != 2:
                raise ValueError("Timer random range needs two specified values.")
            delay = random.randint(self.randRange[0], self.randRange[1])
        if self.timerType == "sec":
            currentSec = time.localtime()[5]
            if (currentSec + delay) > 61:
                self.timeDelay = (currentSec + delay) - 61
            else:
                self.timeDelay = currentSec + delay
        elif self.timerType == "min":
            currentMin = time.localtime()[4]
            if (currentMin + delay) > 59:
                self.timeDelay = (currentMin + delay) - 59
            else:
                self.timeDelay = currentMin + delay

    def check(self):
        if not self.active:
            return False
        
        if self.timerType == "sec":
            state = time.localtime()[5] == self.timeDelay
        elif self.timerType == "min":
            state = time.localtime()[4] == self.timeDelay

        if state:
            if self.loop:
                self.__setDelay(self.rawDelay)
            else:
                self.active = False
                
        return state

# The main loop for bot timers. This will be run in a different thread to
# run in parallel with the main bot.
class _BotTimers:
    __timerList = []

    # These are accesed from outside to change
    initialized = False # Controls the main loop
    active = False      # Controls whether timer functions will run

    def __init__(self):
        self.thread = threading.Thread(target=self.__loop, args=())
        self.initialized = True

    def begin(self):
        self.active = True
        self.thread.start()

    # Creates a timer class, that when reached will activate a callback function
    def addTimer(self, ttype, delay, callback,
                 args, _rand=False, _rrange=(), _loop=False):
        t_entry = {}
        timer = _Timer(ttype, delay, rand=_rand, rrange=_rrange, loop=_loop)

        t_entry['timer'] = timer
        t_entry['callback'] = callback
        t_entry['args'] = args

        self.__timerList.append(t_entry)

    def __loop(self):
        while self.initialized:
            del_q = []
            for entry in self.__timerList:
                if entry['timer'].check() and self.active:
                    entry['callback'](entry['args'])
                if not entry['timer'].active:
                    del_q.append(entry)
            for e in del_q:
                self.__timerList.remove(e)
            time.sleep(1)
            
# General class for the IRC connection. Contains all join and messaging commands
class IRCBot:
    __chat = None    # Socket connection.
    __info = None    # BotInfo instance.

    userlist = []    # All the users in the channel.
    modlist  = []    # All the elevated users, hop and higher.
    owners   = []    # All the owners (will typically be just one if any).

    def __init__(self):
        self.__chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__info = _BotInfo()

    def setInfoFromConfig(self, filename):
        self.__info.parseConfig(filename)

    # The 'getter' functions for interfacing with the info instance
    def currentServer(self):
        return self.__info.server
    def channel(self):
        return self.__info.channel
    def nick(self):
        return self.__info.nick
    def mbid(self):
        return self.__info.mbid
    def source(self):
        return self.__info.sourceCode
    def joinmsg(self):
        return self.__info.joinmsg
    def greenActive(self):
        return self.__info.green
    def checkGreen(self, nick):
        return self.__info.greenNick == nick
    def version(self):
        return self.__info.version
    def isAwake(self):
        return self.__info.state
    def gamesActive(self):
        return self.__info.games

    # 'Setter' functions for the info instance.
    def greenNick(self, nick):
        self.__info.greenNick = nick
    def greenOn(self):
        self.__info.green = True
    def greenOff(self):
        self.__info.green = False
    def wake(self):
        self.__info.state = True
    def sleep(self):
        self.__info.state = False
    def activateGames(self):
        self.__info.games = True
    def deactivateGames(self):
        self.__info.games = False
    def activateJoinMsg(self):
        self.__info.joinmsg = True
    def deactivateJoinMsg(self):
        self.__info.joinmsg = False

    # Timer controls
    def initializeTimers(self):
        self.__timers = _BotTimers()
    def timersInitialized(self):
        return self.__timers is not None
    def startTimers(self):
        self.__timers.begin()
    def pauseTimers(self):
        self.__timers.active = False
    def resumeTimers(self):
        self.__timers.active = True
    def killTimers(self):
        self.__timers.initialized = False        
    def addTimer(self, ttype, delay, callback,
                 args, rand=False, rrange=(), loop=False):
        self.__timers.addTimer(ttype, delay, callback, args,
                               _rand=rand, _rrange=rrange, _loop=loop)
        
    def start(self):
        self.__info.verifyConfig()
        
        print("Connecting to %s." % self.__info.server)
        
        self.__connectServer(self.__info.server)
        self.__identify(self.__info.password)
        self.__connectNick(self.__info.nick)
        self.__connectUser(self.__info.nick, "Hello")

        # Here we wait until the server prompts to enter the password.
        unregistered = True
        while unregistered:
            text = ''
            try:
                text = self.__getText()

                try:
                    print(text)
                except UnicodeEncodeError:
                    None
            except socket.timeout:
                None

            if text.lower().find('identify') != -1:
                unregistered = False

        self.__identify(self.__info.password)
        print("Bot nick set as %s." % self.__info.nick)
        print("Joining channel %s." % self.__info.channel)

        self.__join(self.__info.channel)

    # Channel setup.
    def setUser(self, nick):
        self.__info.nick = nick
    def setChannel(self, chan):
        self.__info.channel = chan
    def setServer(self, serv):
        self.__info.server = serv
    def setPassword(self, password):
        self.__info.password = password

    # Internal connection initializations.
    def __connectServer(self, server):
        self.__chat.connect((server, 6667))
    def __connectUser(self, name, message):
        self.__chat.send(("USER %s botnick botnick :%s\r\n" % (name, message)).encode('utf-8'))
    def __connectNick(self, nick):
        self.__chat.send(("NICK %s\r\n" % nick).encode('utf-8'))
    def __identify(self, password):
        self.__chat.send(("PRIVMSG nickserv :identify %s\r\n" % password).encode('utf-8'))
    def __join(self, channel):
        self.__chat.send(("JOIN %s\r\n" % channel).encode('utf-8'))

    def __getText(self):
        return self.__chat.recv(2048).decode('utf-8')

    # Formats and prepares an IRCMessage instance to return.
    # Also updates the userlists if applicable.
    def incoming(self):
        text = self.__getText().strip()
        
        if text.find("PING") != -1:
            self.__chat.send(("PONG %s\r\n" % (text.split()[1])).encode('utf-8'))
        else:
            try:
                print(text)
            except UnicodeDecoreError:
                None
            
        for line in text.split('\n'):
            message = IRCMessage(line)
            if message.IRCcmd == '353':
                self.__setUserList(message)
            elif message.IRCcmd == 'PART' or message.IRCcmd == 'QUIT':
                self.__removeUser(message.nick)
            elif message.IRCcmd == 'JOIN':
                self.__appendUser(message.nick)
            elif message.IRCcmd == 'MODE':
                self.__updateUser(message.IRCparams)

        # Only returns the last message for checking
        return message
    
    # Bot interaction commands.
    def msg(self, message):
        self.__chat.send(("PRIVMSG %s :%s\r\n" % (self.__info.channel, message)).encode('utf-8'))
    def kick(self, nick,  message):
        self.__chat.send(("KICK %s %s :%s\r\n" % (self.__info.channel, nick, message)).encode('utf-8'))
    def quitirc(self, message):
        self.__chat.send(("QUIT :Quit %s\r\n" % message).encode('utf-8'))
    def memo(self, nick, message):
        self.__chat.send(("PRIVMSG memoserv :send %s %s\r\n" 
                        % (nick, message)).encode('utf-8'))
    def action(self, message):
        self.msg("\x01ACTION %s" % message)

    # Userlist commands
    def __appendUser(self, nick):
        if len(nick) < 1:
            return
        
        nick = nick.strip()
        
        if nick[0] in ('%', '@', '&'):
            nick = nick[1:]
            if nick not in self.modlist:
                self.modlist.append(nick)
        elif nick[0] == '~':
            nick = nick[1:]
            if nick not in self.modlist or nick not in self.owners:
                self.modlist.append(nick)
                self.owners.append(nick)

        if nick not in self.userlist:
            self.userlist.append(nick)

    def __removeUser(self, nick):
        nick = nick.strip()
        
        if nick in self.userlist:
            self.userlist.remove(nick)
        if nick in self.modlist:
            self.modlist.remove(nick)
        if nick in self.owners:
            self.owners.remove(nick)

    def __updateUser(self, IRCparams):
        if len(IRCparams) < 3:
            return

        modeset = IRCparams[1]
        nick    = IRCparams[2].strip()

        if modeset.startswith('+'):
            if 'o' in modeset or 'a' in modeset or 'h' in modeset:
                if nick not in self.modlist:
                    self.modlist.append(nick)
            if 'q' in modeset:
                if nick not in self.owners:
                    self.owners.append(nick)
        elif modeset.startswith('-'):
            if 'o' in modeset or 'a' in modeset or 'h' in modeset:
                if nick in self.modlist:
                    self.modlist.remove(nick)
            elif 'q' in modeset:
                if nick in self.owners:
                    self.owners.remove(nick)

    def __setUserList(self, text):
        for nick in text.body.split(' '):
            self.__appendUser(nick)
