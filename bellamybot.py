'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
BellamyBot v2.1.0 created by Kueller917.
Intended for use in the python2 engine, yes I know it's outdated.
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
import txtfunctions
import musegames
import setlistgenerator
import timercommands
from random import randint
from threading import Timer

# This setup part was copied from the internet without credit
server = "irc.rizon.net"
channel = "#muse"
botnick = "BellamyBot"
password = ""

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to %s" % (server))

# Connect to server, identify nick, and join channel
irc.connect((server, 6667))
irc.send('USER Bellamy botnick botnick :Hello\r\n')
irc.send('NICK %s\n' % (botnick))
irc.send('PRIVMSG nickserv :identify %s\r\n' % (password))
irc.send('JOIN %s\r\n' % (channel))

irc.send('PRIVMSG %s :Hello!\r\n' % (channel))

# Global variables
owner = ('Kueller917', 'Kueller')
ops = ('Kueller917', 'Kueller', 'ryanp16', 'fabripav')
ircmsg = ('PRIVMSG %s' % (channel))
sourceCode = 'http://waa.ai/43iV'

botstate = False

crowdChoice = randint(1,5)

# Commands to be run on timer signals
# Crowd choice opens up requests for a randomly chosen song, 
# Starts a new one minute timer
def crowd_choice_start():
    if (botstate):
        irc.send('%s :Crowd choice! Type !choice and your ' % (ircmsg))
        irc.send('song to play.\r\n')
        Timer(60, crowd_choice_print).start()
        crowd_choice_start.CROWD_ON = True

# After one minute, print a random song from the requested list
def crowd_choice_print():
    if (botstate):
        songChoice = timercommands.crowd_choice()
        irc.send('%s :%s\r\n' % (ircmsg, songChoice))
        crowd_choice_start.CROWD_ON = False

# Chooses a random phrase to say
def phrase():
    if (botstate):
        phrase = timercommands.random_phrase()
        irc.send('%s :%s\r\n' % (ircmsg, phrase))

# A game of Russian roulette triggered by a command
# Continuously calls the function in the style of a state machine
def russia():
    if (botstate):
        if (russia.state == 0):
            Timer(2, russia).start()
            russia.state = 1
            irc.send('%s :\x01ACTION spins cylinder\r\n' % (ircmsg))
        elif (russia.state == 1):
            Timer(2, russia).start()
            russia.state = 2
            irc.send('%s :\x01ACTION aims at %s\r\n' % (ircmsg, russia.nick))
        elif (russia.state == 2):
            Timer(4, russia).start()
            russia.state = 3
            irc.send('%s :\x01ACTION pulls trigger\r\n' % (ircmsg))
        elif (russia.state == 3):
            if (russia.cylinder == 6):
                irc.send('KICK %s %s :BANG!\r\n' % (channel, russia.nick))
                irc.send('%s :He didn\'t fly so good. ' % (ircmsg))
                irc.send('Who wants to try next?\r\n')
            else:
                irc.send('%s :You got lucky this time.\r\n' % (ircmsg))
            russia.state = 0

# Timer function variables
crowd_choice_start.CROWD_ON = False
russia.cylinder = 0
russia.state = 0
russia.nick = None

# Timer initializations. Does not go over 9000.
phrase_1 = Timer(randint(1200,1800), phrase)
phrase_2 = Timer(randint(2400,3000), phrase)
phrase_3 = Timer(randint(4500,4800), phrase)
phrase_4 = Timer(randint(5700,6000), phrase)
phrase_5 = Timer(randint(7200,7800), phrase)
phrase_6 = Timer(randint(8700,9000), phrase)
crowd_timer = Timer(3600, crowd_choice_start)

print('TIMERS INITIALIZED')
print('CROWD CHOICE %d' % (crowdChoice))

def main():
    global botstate

    green = False
    joinmsg = False
    greenNick = None

    BOT_ON = True

    while (BOT_ON):
        text = irc.recv(2040)
        print(text)
        if text.find('PING') != -1:
            irc.send('PONG %s\r\n' % (text.split()[1]))
        if text.find(':Hello %s' % (botnick)) != -1:
            irc.send('%s :Hello %s\r\n' % (ircmsg, nick))

        # Join greeting, can be turned on/off, is state dependent
        if (text.split(' ')[1] == 'JOIN') and (joinmsg) and (botstate):
            nick = text.split('!')[0].replace(':','')
            irc.send('%s :Welcome to the sexy plane %s. ' % (ircmsg, nick))
            irc.send('Enter !commands to view the bot functions.\r\n')

        # Commands
        if text.find('PRIVMSG') != -1:
            nick = text.split('!')[0].replace(':','')
            chan = text.split(' ')[2]
            chanmsg = text.split(':')[2]
            botmsg = chanmsg.partition(' ')
            command = botmsg[0]
            argument = botmsg[2]

            if nick in owner:
                if (command == '!shutdown\r\n'):
                    irc.send('%s :Shutting down!\r\n' % (ircmsg))
                    irc.send('QUIT :I\'ve seen all I\'ll ever need.\r\n')
                    sys.stdout.write('Quit IRC. Deactivating timers...')

                    phrase_1.cancel()
                    phrase_2.cancel()
                    phrase_3.cancel()
                    phrase_4.cancel()
                    phrase_5.cancel()
                    phrase_6.cancel()
                    crowd_timer.cancel()
                    sys.stdout.write('\t[DONE]\nExiting program\n')
                    
                    BOT_ON = False
                
            # OP only commands
            if nick in ops:
                
                # Bot state commands
                # Also activates/deactivates timers
                if command == '!wake\r\n':
                    botstate = True
                    phrase_1.start()                       
                    phrase_2.start()
                    phrase_3.start()
                    phrase_4.start()
                    phrase_5.start()
                    phrase_6.start()
                    if (crowdChoice == 5):
                        crowd_timer.start()

                    irc.send('%s :BellamyBot is online.\r\n' % (ircmsg))
                    
                if command == '!sleep\r\n':
                    botstate = False
                    phrase_1.cancel()
                    phrase_2.cancel()
                    phrase_3.cancel()
                    phrase_4.cancel()
                    phrase_5.cancel()
                    phrase_6.cancel()
                    crowd_timer.cancel()
                    irc.send('%s :Sleep mode activated\r\n' % (ircmsg))
                    
                if command == '!joinmsg':
                    if (argument == 'on\r\n'):
                        joinmsg = True
                        print('Join messages ON')
                    elif (argument == 'off\r\n'):
                        joinmsg = False
                        print('Join messages OFF')

                if command == '!setgig':
                    gigText = open('gig', 'w')
                    gigText.write(argument)
                    gigText.close()

                # Setlist controls
                if command == '!add':
                    txtfunctions.add_song(argument)

                if command == '!clearset\r\n':
                    setlistText = open('setlist', 'w')
                    setlistText.write('')
                    setlistText.close()
                    
                    irc.send('%s :Current setlist has been cleared\r\n'\
                                                             % (ircmsg))

                if command == '!undo\r\n':
                    filename = 'setlist'
                    txtfunctions.song_undo(filename)
                    irc.send('%s :The last song has been erased\r\n'\
                                                          % (ircmsg))

                if command == '!replace':
                    response = txtfunctions.replace_song(argument)
                    irc.send('%s :%s\r\n' % (ircmsg, response))
                
                if command == '!delete':
                    reponse = txtfunctions.delete_song(argument)
                    irc.send('%s :%s\r\n' % (ircmsg, response))
                    
                if command == '!setprevious\r\n':
                    response = txtfunctions.set_previous()
                    irc.send('%s :%s\r\n' % (ircmsg, response))
                
            # All user commands
            if command == '!bot\r\n':
                irc.send('%s :BellamyBot version 2.1.0 created by ' % (ircmsg))
                irc.send('Kueller917. Status: ')
                if (botstate):
                    irc.send('ONLINE.\r\n')
                else:
                    irc.send('OFFLINE.\r\n')
            
            if command == '!gig\r\n':
                gigText = open('gig', 'r')
                gig = gigText.read()
                irc.send('%s :%s\r\n' % (ircmsg, gig))
                gigText.close()

            if command == '!message':
                memoText = open('ircmsg', 'a')
                memoText.write('%s: %s' % (nick, argument))
                memoText.close()

                irc.sned('PRIVMSG memoserv :send Kueller917 You have a message')
                irc.send(' from %s\r\n' % (nick))

            if command == '!source\r\n':
                irc.send('%s :Get your own copy of BellamyBot today!'\
                                                           % (ircmsg))
                irc.send(' %s\r\n' % (sourceCode))

            # State dependent commands
            if (botstate):
                
                # General commands
                if command == '!setlist\r\n':
                    filename = 'setlist'
                    irc.send('%s :CURRENT SETLIST: ' % (ircmsg))
                    
                    currentset = txtfunctions.print_set(filename)

                    if currentset == '':
                        current = '...is empty'
                    irc.send('%s\r\n' % (currentset))

                if command == '!previousset\r\n':
                    filename = 'previous'
                    previous = txtfunctions.print_set(filename)
                    irc.send('%s :%s\r\n' % (ircmsg, previous))

                if command == '!commands\r\n':
                    irc.send('%s :' % (ircmsg))
                    irc.send('Use !gig, !setlist and !previousset for \
                    information on tonight\'s concert. Try !rotation, \
                    !closer, !manson, !roulette, !setgen, !ru-roulette\
                     and !realfun for fun.\r\n')
                
                # Games
                if command == '!closer\r\n':
                    closer = musegames.random_game('gigcloser')
                    irc.send('%s :%s\'s game has closed with %s.\r\n'\
                                             % (ircmsg, nick, closer))

                if command == '!opener\r\n':
                    opener = musegames.random_game('opener')
                    irc.send('%s :%s\'s game has opened with %s.\r\n'\
                                             % (ircmsg, nick, opener))

                if command == '!realfan\r\n':
                    fan = randint(0,1)
                    if (fan):
                        irc.send('%s :%s is a REAL FAN. Good for you'\
                                                     % (ircmsg, nick))
                        irc.send('\r\n')
                    else:
                        irc.send('%s :%s is not a REAL FAN. Go away.'\
                                                     % (ircmsg, nick))
                        irc.send('\r\n')

                if command == '!ru-roulette\r\n':
                    russia.cylinder = randint(1,6)
                    russia.nick = nick
                    
                    print('RUSSIAN ROULETTE FROM %s' % (nick))
                    print('RANDOM COUNT %d' % (russia.cylinder))

                    russia()

                if command == '!choice':
                    if (crowd_choice_start.CROWD_ON):
                        selection = txtfunctions.acronym_replace(argument)

                        crowdText = open('crowd', 'a')
                        crowdText.write('%s\n' % (selection))
                        crowdText.close()

                if command == '!roulette\r\n':
                    output = musegames.T2L_roulette()
                    if (output):
                        irc.send('%s :%s\r\n' % (ircmsg, output))
                    else:
                        irc.send('%s :You landed on GREEN!' % (ircmsg))
                        irc.send(' Type !green to get your song!\r\n')

                        green = True
                        greenNick = nick

                if command == '!green\r\n':
                    if (green):
                        if (nick == greenNick):
                            irc.send('%s :%s\r\n'\
                             % (ircmsg, musegames.roulette_green(nick)))

                            green = False
                            greenNick = None
                        else:
                            irc.send('%s :' % (ircmsg))
                            irc.send('You did not land on green.\r\n')

                if command == '!manson\r\n':
                    mansons = musegames.manson_game(nick)
                    irc.send('%s :%s\r\n' % (ircmsg, mansons))

                if command == '!setgen\r\n':
                    randomset = setlistgenerator.generate()
                    randomsize = len(randomset)

                    if (randomsize == 2):
                        irc.send('%s :%s\r\n' % (ircmsg, randomset[0]))
                        irc.send('%s :ENCORE: %s\r\n'  % (ircmsg, randomset[1]))

                    elif (randomsize == 3):
                        irc.send('%s :%s\r\n' % (ircmsg, randomset[0]))
                        irc.send('%s :ENCORE 1: %s\r\n' \
                                % (ircmsg, randomset[1]))
                        irc.send('%s :ENCORE 2: %s\r\n' \
                                % (ircmsg, randomset[2]))

    return 0

if __name__ == "__main__":
    main()

                
        


