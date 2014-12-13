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
    phrase.replace("%d", "%d" % random.randint(2,20))

    return phrase

# A game of russian roulette
# 1 in 6 chance of getting "shot" (kicked from the channel)
# Increments a series of action in the style of a state machine
class RussianRoulette:
    gameState = None
    gameTimer = None
    gameNick = None
    cylinder = None
    
    def __init__(self, nick):
        self.gameState = 0
        self.gameNick = nick
        self.cylinder = random.randint(1,6)
        self.gameTimer = Timer()
        self.gameTimer.secTimer(0)

        print("New roulette from %s" % nick)
        print("Cylinder: %d" % self.cylinder)

    # Check yourself
    def check(self):
        if self.gameTimer.check():
            if self.gameState == None:
                return None
            elif self.gameState == 0:
                self.gameTimer.secTimer(3)
                self.gameState = 1
                return "\x01ACTION spins cylinder"
            elif self.gameState == 1:
                self.gameTimer.secTimer(3)
                self.gameState = 2
                return ("\x01ACTION points gun at %s" % self.gameNick)
            elif self.gameState == 2:
                self.gameTimer.secTimer(3)
                self.gameState = 3
                return "\x01ACTION pulls trigger"
            elif self.gameState == 3:
                self.gameState = None
                if self.cylinder == 6:
                    return "KICK"
                else:
                    return "You got lucky this time."

    # Kicks user from channel. Requires the irc object to kick user.
    def shoot(self, irc, info):
        if self.gameNick in info.ops:
            irc.msg("You're too important to die")
            return
        
        irc.kick(self.gameNick, "BANG!")
        irc.msg("He didn't fly so good. Who wants to try next?")
