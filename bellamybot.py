'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
BellamyBot v3.2.0 created by Kueller917.
Created for use with Python 3.
Being created for personal use, the processes might not be the most efficient, 
nor the simplest.

You are free to use this file, and any other file of BellamyBot as you wish.
I do not "grant permission" for use as permission is yours by default. 
See LICENSE for more info. However, I do not know why you would want to use 
this. There are better bots.

Nickserv password not included for hopefully obvious reasons.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import sys
import socket
import commands
import filehandle
import txtfunctions
import timercommands
import setlistgenerator
from timers import Timer
from random import randint
from crowdchoice import CrowdChoice
from bellamylib import BotConnection

# Connect to IRC using this information
# I'm planning to change these features with a config file
server = "irc.rizon.net"
channel = "#muse"
botnick = "BellamyBot"
password = ""

irc = BotConnection()

irc.connect(server)
print("Connecting to %s" % server)

irc.setuser("Bellamy", "Hello")
irc.setnick(botnick)
irc.identify(password)
irc.join(channel)

def main():

    # Repeating timer to say a random phrase every 10-20 minutes
    phraseTimer = Timer()
    phraseTimer.minTimer(randint(10,20))

    crowd = CrowdChoice()
    roulette = None
    
    BOT_ON = True

    while (BOT_ON):

        # Timer checks
        if phraseTimer.check():
            try:
                phrase = commands.phrase()
                irc.msg(phrase)
                phraseTimer.minTimer(randint(10,20))
            except IOError as e:
                print(e)

        choiceMsg = crowd.check()
        if choiceMsg != None:
            irc.msg(choiceMsg)

        if roulette != None:
            ruMsg = roulette.check()
            if ruMsg == "KICK":
                roulette.shoot(irc)
            elif ruMsg != None:
                irc.msg(ruMsg)
        
        try:
            text = irc.incoming()

            # These commands require direct access to the IRC class
            # or other values that exist only in main
            if text.command in ("!shutdown\r\n", "!shutdown"):
                irc.msg("Shutting down!")
                irc.quitirc("I\'ve seen all I\'ll ever need")
                print("Exiting program")
                BOT_ON = False

            if text.command == "!message":
                try:
                    filehandle.list_append('text/ircmsg', "%s: %s"
                                           % (text.nick, text.argument))
                except IOError as e:
                    print (e)
                    
                irc.memo("Kueller917", "You have a message from %s" % nick)
                
            if text.command == "!choice" and crowd.isActive():
                crowd.addSong(text.argument)

            if text.command in ("!ru-roulette\r\n", "!ru-roulette"):
                roulette = timercommands.RussianRoulette(text.nick)

            if text.command in ("!setgen\r\n", "!setgen"):
                setlistgenerator.generate(irc)

            # Other general commands are sent to the commands function
            # Exceptions are caught and printed, but do not stop the program
            try:
                message = commands.command_run(text)
                if message != None:
                    irc.msg(message)
            except Exception as e:
                print(e)
 
        except socket.timeout:
            None

    return 0

if __name__ == "__main__":
    main()
