import sys
import txtfunctions
import filehandle
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
def setlist():
    main = ''
    otherEnc = ''
    opener = ''
    songs = ''

# Construct a piece of a setlist from the given song list array
# output will be the current setlist, and the updated will be returned
def set_construct(length, array, output, randlimit):
    i = 0
    while i < length:
        songLine = randint(0, randlimit)
        songEntry = filehandle.remove_nr(array[songLine])
        while ((songEntry in output) or (songEntry in setlist.main) or
               (songEntry in setlist.otherEnc)):
            songLine = randint(0, randlimit)
            songEntry = filehandle.remove_nr(array[songLine])
        if (output == ''):
            output = songEntry
        else:
            output = ("%s, %s" % (output, songEntry))
        i += 1
    return output

# Creates either a standard or final encore of 3 songs
# outEnc works the same as output in set_construct
def enc_construct(outEnc, closer, closelimit):    
    outEnc = set_construct(1, setlist.opener, outEnc, 7)   
    outEnc = set_construct(1, setlist.songs, outEnc, 76)    
    outEnc = set_construct(1, closer, outEnc, closelimit)

    setlist.otherEnc = ''
    return outEnc

# The main setlist generator
def generate():
    firstSetLength = randint(5,7)
    pianoLength = randint(1,3)
    secondSetLength = randint(6,7)
    encoreCount = randint(1,2)

    print('Creating setlist...')
    print('\tFirst length: %d' % (firstSetLength))
    print('\tPiano length: %d' % (pianoLength))
    print('\tSecond length: %d' % (secondSetLength))
    print('\tNumber of encores: %d' % (encoreCount))

    try:
        openers = open('text/opener', 'r')
        songs = open('text/songs', 'r')
        pianos = open('text/piano', 'r')
        setcloser = open('text/setcloser', 'r')
        gigcloser = open('text/gigcloser', 'r')
    except:
        print("Error opening files")
        return 0

    openerArray = openers.readlines()
    songsArray = songs.readlines()
    pianoArray = pianos.readlines()
    setCloserArray = setcloser.readlines()
    gigCloserArray = gigcloser.readlines()

    randomSet = ''
    firstEncore = ''
    secondEncore = ''

    setlist.main = ''
    setlist.otherEnc = ''
    setlist.opener = openerArray
    setlist.songs = songsArray

    try:
        randomSet = set_construct(1, openerArray, randomSet, 7)
    
        print("Generating first section...")
        randomSet = set_construct(firstSetLength, songsArray, randomSet, 76)

        print("Generating piano section...")
        randomSet = set_construct(pianoLength, pianoArray, randomSet, 14)

        print("Generating second section...")
        randomSet = set_construct(secondSetLength, songsArray, randomSet, 76)

        print("Closing main set...")
        randomSet = set_construct(1, setCloserArray, randomSet, 14)
    except:
        print("Error creating setlist")
        return 0

    print('Beginning first encore...')
    setlist.main = randomSet
    setlist.opener = openerArray
    setlist.songs = songsArray

    if encoreCount == 1:
        try:
            setlist.otherEnc = secondEncore
            firstEncore = enc_construct(firstEncore, gigCloserArray, 7)
            finalSet = randomSet, firstEncore
            print("Encore 1 of 1 complete...")
        except:
            print("Error creating first encore")
            return 0

    elif encoreCount == 2:
        try:
            setlist.otherEnc = secondEncore
            firstEncore = enc_construct(firstEncore, setCloserArray, 14)
            print('Encore 1 of 2 complete...')
        except:
            print("Error creating first encore")
            return 0

        try:
            setlist.otherEnc = firstEncore
            secondEncore = enc_construct(secondEncore, gigCloserArray, 7)
            finalSet = randomSet, firstEncore, secondEncore
            print('Encore 2 of 2 complete...')
        except:
            print("Error creating second encore")
            return 0

    openers.close()
    songs.close()
    pianos.close()
    setcloser.close()
    gigcloser.close()

    setlist.main = ''
    setlist.otherEnc = ''

    print('Setlist completed')
    return finalSet
