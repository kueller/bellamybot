import txtfunctions
import time
from random import randint

# To work with timers, this creates a minute value after
# the current time. Can be checked with localtime
# in other functions
def delay(minutes):
    currentMin = time.localtime()[4]
    if ((currentMin + minutes) > 59):
        newMin = (currentMin + minutes) - 59
    else:
        newMin = currentMin + minutes
    return newMin

# Same as delay but specifically for the russian roulette
# Creates a timer of 3 seconds
def ru_delay():
    currentSec = time.localtime()[5]
    if ((currentSec + 3) > 61):
        newSec = (currentSec + 3) - 61
    else:
        newSec = currentSec + 3
    return newSec

# If crowd choice is activated, this will choose a random crowd suggestion
# Returns 0 if there's an error
def crowd_choice():
    try:
        crowdText = open('text/crowd', 'r')
        crowdList = crowdText.readlines()
        crowdLength = len(crowdList)
        crowdText.close()
    except:
        print("Error opening crowd_choice files")
        return 0

    if (crowdLength > 0):
        choice = randint(0, crowdLength)
        songChoice = crowdList[choice]
        songChoice = songChoice.split('\n')[0]

        outputString = "I have decided to play %s" % (songChoice)

    else:
        outputString = "No one gave suggestions so I'll play Guiding Light "\
                        "instead."

    try:
        crowdText = open('text/crowd', 'w')
        crowdText.write('')
        crowdText.close()
    except:
        print("Error clearing crowd_choice files")
        return 0

    return outputString

# Says a random phrase from ".botphrases"
# Returns 0 if there's an error
def random_phrase():
    try:
        randomText = open('text/botphrases', 'r')
        randomList = randomText.readlines()
        phraseLength = len(randomList)
        randomText.close()
    except:
        print("Error opening random_phrase file")
        return 0

    throw = randint(1,3)

    if (throw != 3):
        line = randint(0, phraseLength - 1)
        phrase = randomList[line]
        phrase = phrase.split('\n')[0]
    else:
        phrase = '\x01ACTION throws %d Musos into the air' % randint(2,20)

    return phrase
