import sys
import socket

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

        try:
            self.chan = text.split(' ')[2]
        except:
            None

        try:
            self.msg = text.split(':')[2]
            self.command = self.msg.split(' ')[0]
        except:
            None

        try:
            self.argument = self.msg.partition(' ')[2]
        except:
            None

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
# This will also be connected with config files in the future
class BotInfo:
    green = False
    joinmsg = False
    greenNick = None

    sourceCode = "http://waa.ai/4m8N"
    owner = ("Kueller917", "Kueller")
    ops = ("Kueller917", "Kueller", "ryanp16", "fabripav")

    state = False
