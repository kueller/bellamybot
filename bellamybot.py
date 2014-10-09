'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
BellamyBot v3.1.0 created by Kueller917.
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
import time
import socket
import txtfunctions
import musegames
import setlistgenerator
import timercommands
from random import randint

# This setup part was copied from the internet without credit
server = "irc.rizon.net"
channel = "#muse"
botnick = "BellamyBot"
password = ""

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to %s" % (server))

# Connect to server, identify nick, and join channel
irc.connect((server, 6667))
irc.settimeout(1)

irc.send(("USER Bellamy botnick botnick :Hello\r\n").encode('utf-8'))
irc.send(("NICK %s\n" % (botnick)).encode('utf-8'))
irc.send(("PRIVMSG nickserv :identify %s\r\n" % (password)).encode('utf-8'))
irc.send(("JOIN %s\r\n" % (channel)).encode('utf-8'))

irc.send(("PRIVMSG %s :Hello!\r\n" % (channel)).encode('utf-8'))

# Global variables
owner = ("Kueller917", "Kueller")
ops = ('Kueller917', "Kueller", "ryanp16", "fabripav")
sourceCode = "http://waa.ai/4m8N"

botstate = False

crowdChoice = randint(1,5)

# Functions for simple looking IRC commands
def ircmsg(message):
    irc.send(("PRIVMSG %s :%s\r\n" % (channel, message)).encode('utf-8'))

def irckick(nick, message):
    irc.send(("KICK %s %s :%s\r\n" % (channel, nick, message)).encode('utf-8'))

def ircquit(message):
    irc.send(("QUIT :Quit: %s\r\n" % (message)).encode('utf-8'))

def ircmemo(nick, message):
    irc.send(("PRIVMSG memoserv :send %s %s\r\n" 
             % (nick, message)).encode('utf-8'))

# Commands to be run on timer signals
# Crowd choice opens up requests for a randomly chosen song, 
# Starts a new one minute timer
def crowd_choice_start():
    if (botstate):
        ircmsg("Crowd choice! Type !choice and your song to play.")
        crowd_choice_start.CROWD_ON = True

# After one minute, print a random song from the requested list
def crowd_choice_print():
    if (botstate):
        songChoice = timercommands.crowd_choice()
        if songChoice:
            ircmsg("%s" % (songChoice))
        crowd_choice_start.CROWD_ON = False

# Chooses a random phrase to say
def phrase():
    if (botstate):
        phrase = timercommands.random_phrase()
        if phrase:
            ircmsg("%s" % (phrase))

# A game of Russian roulette triggered by a command
# Continuously calls the function in the style of a state machine
def russia():
    if (botstate):
        if (russia.state == 0):
            russia.state = 1
            ircmsg("\x01ACTION spins cylinder")
        elif (russia.state == 1):
            russia.state = 2
            ircmsg("\x01ACTION aims at %s" % (russia.nick))
        elif (russia.state == 2):
            russia.state = 3
            ircmsg("\x01ACTION pulls trigger")
        elif (russia.state == 3):
            if (russia.cylinder == 6):
                irckick(russia.nick, "BANG!")
                ircmsg("He didn\'t fly so good. Who wants to try next?")
            else:
                ircmsg("You got lucky this time.")
            russia.state = 0
            russia.on = False

# Timer function variables
crowd_choice_start.CROWD_ON = False
crowd_choice_start.timer = 0
russia.cylinder = 0
russia.state = 0
russia.nick = None
russia.on = False

print("Crowd choice %d" % (crowdChoice))

def main():
    global botstate

    green = False
    joinmsg = False
    greenNick = None
    
    phrase_timer = timercommands.delay(randint(10,20))
    crowd_init_timer = timercommands.delay(randint(40,50))
    crowd_req_timer = 0
    russia_timer = 0

    BOT_ON = True

    while (BOT_ON):

        # Timer checks
        if (time.localtime()[4] == phrase_timer):
            phrase()
            phrase_timer = timercommands.delay(randint(1,1))

        if (time.localtime()[5] == russia_timer and russia.on):
            russia()
            russia_timer = timercommands.ru_delay()

        if (time.localtime()[4] == crowd_init_timer and crowdChoice == 5):
            crowd_choice_start()
            crowd_req_timer = timercommands.delay(1)

        if (time.localtime()[4] == crowd_req_timer and 
            crowd_choice_start.CROWD_ON):
            crowd_choice_print()

        try:
            text = irc.recv(2048).decode('utf-8')
            print(text)
            if text.find("PING") != -1:
                irc.send(("PONG %s\r\n" % (text.split()[1])).encode('utf-8'))


            # Join greeting, can be turned on/off, is state dependent
            if (text.split(' ')[1] == ("JOIN")
               and (joinmsg) and (botstate)):
                nick = text.split('!')[0].replace(':','')
                ircmsg("Welcome to the sexy plane %s. "
                       "Enter !commands to view the bot functions." % (nick))

            # Commands
            if text.find("PRIVMSG") != -1:
                nick = text.split('!')[0].replace(':','')
                chan = text.split(' ')[2]
                chanmsg = text.split(':')[2]
                botmsg = chanmsg.partition(' ')
                command = botmsg[0]
                argument = botmsg[2]

                if nick in owner:
                    if (command == "!shutdown\r\n"):
                        ircmsg("Shutting down!")
                        ircquit("I\'ve seen all I\'ll ever need")
                        print("Exiting program")
                        BOT_ON = False

                # OP only commands
                if nick in ops:

                    # Bot state commands
                    # Also activates/deactivates timers
                    if command == "!wake\r\n":
                        botstate = True
                        phrase_timer = timercommands.delay(randint(10,20))
                        crowd_init_timer = timercommands.delay(randint(40,50))

                        ircmsg("BellamyBot is online.")

                    if command == "!sleep\r\n":
                        botstate = False
                        phrase_timer = 0
                        crowd_init_timer = 0
                        ircmsg("Sleep mode activated")

                    if command == "!joinmsg":
                        if (argument == "on\r\n"):
                            joinmsg = True
                            print("Join messages ON")
                        elif (argument == "off\r\n"):
                            joinmsg = False
                            print("Join messages OFF")

                    if command == "!setgig":
                        gigText = open('text/gig', 'w')
                        gigText.write(argument)
                        gigText.close()

                    # Setlist controls
                    if command == "!add":
                        txtfunctions.add_song(argument)

                    if command == "!clearset\r\n":
                        setlistText = open('text/setlist', 'w')
                        setlistText.write('')
                        setlistText.close()

                        ircmsg("Current setlist has been cleared")

                    if command == "!undo\r\n":
                        if (txtfunctions.song_undo() != -1):
                            ircmsg("The last song has been erased")

                    if command == "!replace":
                        response = txtfunctions.replace_song(argument)
                        if (response != -1):
                            ircmsg("%s" % (response))

                    if command == "!delete":
                        response = txtfunctions.delete_song(argument)
                        if response:
                            ircmsg("%s" % (response))

                    if command == "!setprevious\r\n":
                        response = txtfunctions.set_previous()
                        if response:
                            ircmsg("%s" % (response))

                # All user commands
                if command == "!bot\r\n":
                    stateStr = ("BellamyBot version 3.1.0 created by "
                                "Kueller917. Status:")
                    if (botstate):
                        ircmsg("%s ONLINE." % (stateStr))
                    else:
                        ircmsg("%s OFFLINE" % (stateStr))

                if command == "!gig\r\n":
                    gigText = open('text/gig', 'r')
                    gig = gigText.read()
                    ircmsg("%s" % (gig))
                    gigText.close()

                # Note: I'm aware the file "ircmsg" can be confused
                # with the function of the same name. I'll fix it... later
                if command == "!message":
                    memoText = open('text/ircmsg', 'a')
                    memoText.write("%s: %s" % (nick, argument))
                    memoText.close()

                    ircmemo("Kueller917", ("You have a message from %s" 
                                           % (nick)))

                if command == "!source\r\n":
                    ircmsg("Get your own copy of BellamyBot "
                           "today! %s" % (sourceCode))

                # State dependent commands
                if (botstate):

                    # General commands
                    if command == "!setlist\r\n":
                        filename = "text/setlist"
                        setStr = "CURRENT SETLIST: "

                        currentset = txtfunctions.print_set(filename)

                        if currentset != -1:
                            if currentset == '':
                                currentset = "...is empty"
                            ircmsg("%s%s" % (setStr, currentset))

                    if command == "!previousset\r\n":
                        filename = "text/previous"
                        previous = txtfunctions.print_set(filename)
                        ircmsg("%s" % (previous))

                    if command == "!commands\r\n":
                        ircmsg("Use !gig, !setlist and !previousset for " 
                               "information on tonight\'s concert. Try "
                               "!rotation, !closer, !manson, !roulette, "
                               "!setgen, !ru-roulette and !realfan for fun.")

                    # Games
                    if command == "!closer\r\n":
                        closer = musegames.random_game("gigcloser")

                        if closer:
                            ircmsg("%s\'s game has closed with %s." % 
                                                      (nick, closer))

                    if command == "!opener\r\n":
                        opener = musegames.random_game("opener")

                        if opener:
                            ircmsg("%s\'s game has opened with %s." % 
                                                      (nick, opener))

                    if command == "!realfan\r\n":
                        fan = randint(0,1)
                        if (fan):
                            ircmsg("%s is a REAL FAN. Good for you" % (nick))
                        else:
                            ircmsg("%s is not a REAL FAN. Go away." % (nick))

                    if command == "!ru-roulette\r\n":
                        russia.cylinder = randint(1,6)
                        russia.nick = nick
                        russia.on = True

                        print("RUSSIAN ROULETTE FROM %s" % (nick))
                        print("RANDOM COUNT %d" % (russia.cylinder))

                        russia()
                        russia_timer = timercommands.ru_delay()

                    if command == "!choice":
                        if (crowd_choice_start.CROWD_ON):
                            selection = txtfunctions.acronym_replace(argument)

                            try:
                                crowdText = open('text/crowd', 'a')
                                crowdText.write("%s\n" % (selection))
                                crowdText.close()
                            except:
                                print("Error writing choice")

                    if command == "!roulette\r\n":
                        output = musegames.T2L_roulette()
                        if (output):
                            ircmsg("%s" % (output))
                        else:
                            ircmsg("You landed on GREEN! "
                                   "Type !green to get your song!")

                            green = True
                            greenNick = nick

                    if command == "!green\r\n":
                        if (green):
                            if (nick == greenNick):
                                ircmsg("%s" % (musegames.roulette_green(nick)))

                                green = False
                                greenNick = None
                            else:
                                ircmsg("You did not land on green.")

                    if command == "!manson\r\n":
                        mansons = musegames.manson_game(nick)
                        if mansons:
                            ircmsg("%s" % (mansons))

                    if command == "!setgen\r\n":
                        randomset = setlistgenerator.generate()

                        if randomset:
                            randomsize = len(randomset)

                            if (randomsize == 2):
                                ircmsg("%s" % (randomset[0]))
                                ircmsg("ENCORE: %s" % (randomset[1]))
                            elif (randomsize == 3):
                                ircmsg("%s" % (randomset[0]))
                                ircmsg("ENCORE 1: %s" % (randomset[1]))
                                ircmsg("ENCORE 2: %s" % (randomset[2]))

        except socket.timeout:
            None

    return 0

if __name__ == "__main__":
    main()
