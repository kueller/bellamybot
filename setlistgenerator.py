import setgenlib
from random import randint

# Setlist generator
# 77 songs                      'songs'
# 8 openers                     'opener'
# 15 piano songs                'piano'
# 15 set closers                'setcloser'
# 8 gig closers                 'gigcloser'

# General set structure:
#
# Opener
# Collection of random songs
# Piano section
# Another collection of songs
# Set closer
#
# Can have either one or two encores
# Each encore will have an opener, random song, and closer
# Final encore will have a gig closer, non-closing encore will have a set closer

# Values that need to be read by different functions

def generate(irc):
    try:
        randomSet = setgenlib.Setlist()
    except IOError as e:
        print(e)
        return
    
    encoreCount = randint(0,1)

    randomSet.constructMainSet()
    
    if encoreCount:
        randomSet.constructTwoEncore()
    else:
        randomSet.constructSingleEncore()

    randomSet.printSet(irc)
