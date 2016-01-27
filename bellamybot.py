'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
BellamyBot v4.1.3 created by Kueller917.
Created for use with Python 3.
Being created for personal use, the processes might not be the most efficient, 
nor the simplest.

You are free to use this file, and any other file of BellamyBot as you wish.
I do not "grant permission" for use as permission is yours by default. 
See LICENSE for more info. However, I do not know why you would want to use 
this. There are better bots.

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import cmd
import twit
import undo
import tweepy
import commands
import filehandle
import timercommands
from random import randint
from bellamylib import IRCBot

def main():

    irc = IRCBot()
    irc.setInfoFromConfig('config')
    irc.start()

    irc.initializeTimers()

    toot = twit.authorize_new_twit('text/twitter')
    currentTweet = twit.get_recent_tweet(toot, 'muse')

    user_commands = cmd.create_commands_from_file('text/commands')
    
    def twitter_check(args):
        try:
            newTweet = twit.get_recent_tweet(toot, 'muse')
            if currentTweet.created_at != newTweet.created_at:
                currentTweet = newTweet
                twit.notify_new_tweet(irc, 'muse', currentTweet)
        except tweepy.error.TweepError:
            print('Twitter read error. Continuing.')

    def phrase_check(args):
        try:
            commands.phrase(irc)
        except IOError as e:
            print(e)

    #irc.addTimer("min", 1, twitter_check, None, loop=True)
    irc.addTimer("min", 0, phrase_check, None, rand=True, rrange=(10,20), loop=True)

    irc.startTimers()
    
    undo.refresh()

    BOT_ON = True

    while (BOT_ON):

        text = irc.incoming()

        # These commands require access to other variables in main.
        if (text.command in ("!shutdown\r\n", "!shutdown")
            and text.nick in irc.owners):
            irc.msg("Shutting down!")
            irc.quitirc("I\'ve seen all I\'ll ever need")
            print("Saving commands to file.")
            cmd.dump_commands_to_file(user_commands, 'text/commands')
            print("Exiting program")
            if irc.timersInitialized():
                irc.killTimers()
            BOT_ON = False

        elif text.command == "!tweet" and text.nick in irc.modlist:
            twit.tweet(toot, text.argument)

        elif text.command == "!retweet" and text.nick in irc.modlist:
            twit.retweet(toot, text.argument)

        # Other general commands are sent to the commands function
        commands.command_run(text, irc, user_commands)
 
if __name__ == "__main__":
    main()
