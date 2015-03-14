import random
import filehandle
from timers import Timer

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
def russian_roulette(irc, nick):
    def roulette_wait():
        t = Timer()
        t.secTimer(3)
        while t.check() is False:
            None

    def roulette_shoot():
        if nick in irc.modlist:
            irc.msg("You're too important to die.")
        else:
            irc.kick(nick, "BANG!")
            irc.msg("He didn't fly so good. Who wants to try next?")
            
    def roulette_loop(i, roll):
        if i == 0:
            irc.msg("\x01ACTION spins cylinder.")
            roulette_wait()
            roulette_loop(i + 1, roll)
        elif i == 1:
            irc.msg("\x01ACTION points gun at %s." % nick)
            roulette_wait()
            roulette_loop(i + 1, roll)
        elif i == 2:
            irc.msg("\x01ACTION pulls trigger.")
            roulette_wait()
            roulette_loop(i + 1, roll)
        elif i == 3:
            if roll == 6:
                roulette_shoot()
            else:
                irc.msg("You got lucky this time.")

    cylinder = random.randint(1,6)
    print("New roulette from %s." % nick)
    print("Cylinder: %d." % cylinder)
    roulette_loop(0, cylinder)
