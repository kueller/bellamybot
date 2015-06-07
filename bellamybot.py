'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
BellamyBot v5.1.0 created by Kueller917.
Created for use with Python 3.
Being created for personal use, the processes might not be the most efficient, 
nor the simplest.

You are free to use this file, and any other file of BellamyBot as you wish.
I do not "grant permission" for use as permission is yours by default. 
See LICENSE for more info. However, I do not know why you would want to use 
this. There are better bots.

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import twit
import commands
import filehandle
import timercommands
from timers import Timer
from random import randint
from bellamylib import IRCBot
from crowdchoice import CrowdChoice

def main():

    irc = IRCBot()
    irc.setInfoFromConfig('config')
    irc.start()

    twitter = twit.authorize_new_twit('text/twitter')
    currentTweet = twit.get_recent_tweet(twitter, 'muse')
    
    # Repeating timer to say a random phrase every 10-20 minutes
    phraseTimer = Timer()
    phraseTimer.minTimer(randint(10,15))

    twitTimer = Timer()
    twitTimer.minTimer(1)

    crowd = CrowdChoice()
    
    BOT_ON = True

    while (BOT_ON):

        # Timer checks
        if phraseTimer.check():
            try:
                commands.phrase(irc)
                phraseTimer.minTimer(randint(10,20))
            except IOError as e:
                print(e)

        if twitTimer.check():
            newTweet = twit.get_recent_tweet(twitter, 'muse')
            if currentTweet.created_at != newTweet.created_at:
                currentTweet = newTweet
                twit.notify_new_tweet(irc, 'muse', currentTweet)
            twitTimer.minTimer(1)

        choiceMsg = crowd.check()
        if choiceMsg != None and irc.info.state:
            irc.msg(choiceMsg)

        text = irc.incoming()

        # These commands require access to other variables in main.
        if (text.command in ("!shutdown\r\n", "!shutdown")
            and text.nick in irc.owners):
            irc.msg("Shutting down!")
            irc.quitirc("I\'ve seen all I\'ll ever need")
            print("Exiting program")
            BOT_ON = False
                
        if text.command == "!choice" and crowd.isActive():
            crowd.addSong(text.argument)

        # Other general commands are sent to the commands function
        commands.command_run(text, irc)
 
    return 0

if __name__ == "__main__":
    main()
