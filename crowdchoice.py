import random
import filehandle
import txtfunctions
from timers import Timer

# If crowd choice is activated, this will choose a random crowd suggestion
def crowd_choice():
    try:
        crowdList = filehandle.get_list('text/crowd')
    except IOError:
        raise IOError("Could not open file for crowd_choice")

    if len(crowdList) > 0:
        songChoice = random.choice(crowdList)
        outputMsg = "I have decided to play... %s!" % (songChoice)
    else:
        outputMsg = ("No one gave suggestions so I'll play Guiding Light instead.")

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

    # Initialize timers and variables. valid is a boolean.
    def __init__(self):
        self.valid = (random.randint(1,5) == 5)
        self.crowdInitTimer = Timer()
        self.crowdInitTimer.minTimer(random.randint(40,50))
        self.crowdActiveTimer = Timer()
        self.crowdActiveTimer.minTimer(1)
        self.active = False

    # In regular periods, check() will check the initialization timer.
    # In active state it will check for the active minute to end.
    def check(self):
        if self.active:
            if self.crowdActiveTimer.check() and self.valid:
                try:
                    songChoice = crowd_choice()
                except IOError as e:
                    print(e)
                    return None

                self.active = False
                self.valid = (random.randint(1,5) == 5)
                self.crowdInitTimer.minTimer(random.randint(40,50))

                return ("%s" % songChoice)
        else:
            if self.crowdInitTimer.check() and self.valid:
                self.crowdActiveTimer.minTimer(1)
                self.active = True

                return ("Crowd choice! Type \"!choice\" and your song to play.")
        return None

    # Adds a song to the choice list during the active minute.
    def addSong(self, song):
        song = txtfunctions.acronym_replace(song)
        if self.active and self.valid:
            try:
                filehandle.list_append('text/crowd', song)
            except IOError as e:
                print(e)

    # I actually don't know why I made this.
    def isActive(self):
        return self.active
