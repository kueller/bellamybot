import commands
import filehandle
import txtfunctions
import timercommands
from timers import Timer
from random import randint

# If crowd choice is activated, this will choose a random crowd suggestion
def crowd_choice():
    try:
        crowdList = filehandle.get_list('text/crowd')
    except IOError:
        raise IOError("Could not open file for crowd_choice")

    crowdLength = len(crowdList)

    if crowdLength > 0:
        choice = randint(0, crowdLength)
        songChoice = crowdList[choice]

        outputMsg = "I have decided to play... %s!" % (songChoice)

    else:
        outputMsg = ("No one gave suggestions so I'll play Guiding Light "
                        "instead.")

    try:
        filehandle.clear_file('text/crowd')
    except IOError:
        raise IOError("Error clearing file in crowd_choice")

    return outputMsg

# On activation will run a crowd choice game in 40-50 minutes
# Chance of happening is 1 in 5
# If the game does start, it receives crowd choices for one minute
# At the end a random song will be grabbed using crowd_choice
class CrowdChoice:
    valid = None
    active = None
    crowdInitTimer = None
    crowdActiveTimer = None

    def __init__(self):
        self.valid = (randint(1,5) == 5)
        self.crowdInitTimer = Timer()
        self.crowdInitTimer.minTimer(randint(40,50))
        self.active = False

    def check(self):
        if self.active:
            if (self.crowdActiveTimer.check()
                and commands.bot.state
                and self.valid):

                try:
                    songChoice = crowd_choice()
                except IOError as e:
                    print(e)
                    return None

                self.active = False
                self.valid = (randint(1,5) == 5)
                self.crowdInitTimer.minTimer(randint(40,50))

                return ("%s" % songChoice)
        else:
            if (self.crowdInitTimer.check()
                and commands.bot.state
                and self.valid):

                self.crowdActiveTimer = Timer()
                self.crowdActiveTimer.minTimer(1)
                self.active = True

                return ("Crowd choice! "
                        "Type !choice and your song to play.")
        return None

    def addSong(self, song):
        song = txtfunctions.acronym_replace(song)
        if self.active and self.valid:
            try:
                filehandle.list_append('text/crowd', song)
            except IOError as e:
                print(e)
            
    def isActive(self):
        return self.active
    
    
