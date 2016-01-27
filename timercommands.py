import random
import filehandle

# Says a random phrase from "botphrases"
# Passes on the exception if there was an problem with the text file
def random_phrase():
    try:
        randomList = filehandle.get_list('text/botphrases')
    except IOError:
        raise IOError("Error opening file from random_phrase")
    
    phrase = random.choice(randomList)
    phrase = phrase.replace("%d", "%d" % random.randint(2,20))
    phrase = phrase.encode().decode("unicode_escape")

    return phrase

# A game of russian roulette
# 1 in 6 chance of getting "shot" (kicked from the channel)
# Increments a series of action in the style of a state machine

def roll_1(irc):
    irc.msg("\x01ACTION spins cylinder.")
def roll_2(args):
    irc = args[0]
    nick = args[1]
    irc.msg("\x01ACTION points gun at %s." % nick)
def roll_3(irc):
    irc.msg("\x01ACTION pulls trigger.")
def roll_shoot(args):
    irc = args[0]
    nick = args[1]
    shoot = args[2]
    if shoot:
        if nick in irc.modlist:
            irc.msg("You're too important to die.")
        else:
            irc.kick(nick, "BANG!")
    else:
        irc.msg("You got lucky this time.")

def russian_roulette(irc, nick):
    cylinder = random.randint(1,6) == 6
    roll_1(irc)
    irc.addTimer("sec", 2, roll_2, [irc, nick])
    irc.addTimer("sec", 4, roll_3, irc)
    irc.addTimer("sec", 7, roll_shoot, [irc, nick, cylinder])
