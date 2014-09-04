import os
import sys

# Set this as the file path to write the archive files to
# Whatever directory default files are written to should be considered 
# the root directory
# The filepath should include any directories after it
filepath = "GigArchive/"

# Allows for replacement of acronym entries
def acronym_replace(entry):
    entry = entry.split('\n')[0]
    entry = entry.split('\r')[0]
    if entry == 'B&H':
        entry = 'Butterflies & Hurricanes'
    elif entry == 'CoD':
        entry = 'City of Delusion'
    elif entry == 'FAWY':
        entry = 'Falling Away With You'
    elif entry == 'HTAILY':
        entry = 'Hate This & I\'ll Love You'
    elif entry == 'IBTY':
        entry = 'I Belong To You'
    elif entry == 'IS':
        entry = 'Isolated System'
    elif entry == 'KoC':
        entry = 'Knights of Cydonia'
    elif entry == 'MotP':
        entry = 'Map of the Problematique'
    elif entry == 'NSC':
        entry = 'Neutron Star Collision'
    elif entry == 'PiB':
        entry = 'Plug In Baby'
    elif entry == 'RBS':
        entry = 'Ruled By Secrecy'
    elif entry == 'SMBH':
        entry = 'Supermassive Black Hole'
    elif entry == 'TaB':
        entry = 'Take A Bow'
    elif entry == 'TIRO':
        entry = 'Time Is Running Out'
    elif entry == 'TOADA':
        entry = 'Thoughts of a Dying Atheist'
    return entry

# Remove newline and return characters from an entry
def remove_newline_return(string):
    string = string.split('\n')[0]
    string = string.split('\r')[0]
    return string

# Adds a song, or string of songs, to the .setlist file
# Returns 0 if there's an error
def add_song(argument):
    songList = argument.split(', ')
    songCount = len(songList)
    try:
        setlistText = open('text/setlist', 'a')
    except:
        print("Error opening setlist file")
        return 0

    if songCount == 1:
        songList[0] = acronym_replace(songList[0])
        setlistText.write('%s\n' % songList[0])
    else:
        i = 0
        while i < (songCount - 1):
            songList[i] = acronym_replace(songList[i])
            setlistText.write('%s\n' % songList[i])
            i += 1
        songList[i] = acronym_replace(songList[i])
        setlistText.write('%s\n' % songList[i])
    setlistText.close()

# Removed the most recently entered song from the .setlist file
# Returns 0 if there's an error
def song_undo(filename):
    try:
        fileText = open(filename, 'r')
    except:
        print("Error opening file to read for song_undo")
        return 0

    fileList = fileText.readlines()
    fileSize = len(fileList)
    undoValue = fileSize - 1
    del fileList[undoValue]
    fileText.close()

    try:
        fileText = open(filename, 'w')
        fileText.write('')
    except:
        print("Error opening file to clear for song_undo")
        return 0

    i = 0
    while i < undoValue:
        fileText.write('%s' % fileList[i])
        i += 1
    fileText.close()

# Prints any setlest fed into it and returns a string to be messaged
# Returns -1 if there's an error (Note: only function to not return error 0)
def print_set(filename):
    try:
        fileText = open(filename, 'r')
    except:
        print("Error opening file for print_set")
        return -1
    fileList = fileText.readlines()
    fileSize = len(fileList)

    if fileSize == 0:
        print('EMPTY SETLIST')
        listFinal = ''
    else:
        currentSong = fileList[0]
        currentSong = remove_newline_return(currentSong)
        listFinal = currentSong

        # Extra formatting to print "previous setlist"
        if (filename == 'previous'):
            listFinal = '%s: ' % (currentSong)

            currentSong = fileList[1]
            currentSong = remove_newline_return(currentSong)
            listFinal = '%s%s' % (listFinal, currentSong)

            i = 2
            while i < fileSize:
                currentSong = fileList[i]
                currentSong = remove_newline_return(currentSong)
                listFinal = '%s, %s' % (listFinal, currentSong)
                i += 1

        else:
            i = 1
            while i < fileSize:
                currentSong = fileList[i]
                currentSong = remove_newline_return(currentSong)
                listFinal = '%s, %s' % (listFinal, currentSong)
                i += 1
        fileText.close()

    return listFinal

# Copies the gig and setlist to a previous setlist file
# Then copies the previous setlist to an archive with the gig as the file name
# Returns 0 if there's an error
def set_previous():
    outputString = ''
    try:
        setlistText = open('text/setlist', 'r')
        gigText = open('text/gig', 'r')
    except:
        print("Error opening files for set_previous")
        return 0

    setlist = setlistText.readlines()
    gig = gigText.readlines()
    print('GIG: %s' % (gig))

    setlistText.close()
    gigText.close()

    if (len(gig) == 0):
        print('SetPrevious Error: GIG not found')
        outputString = 'ERROR: No gig set.'
        return outputString
    if (len(setlist) == 0):
        print('SetPrevious Error: Empty setlist')
        outputString = 'ERROR: Setlist is empty.'
        return outputString

    gig = gig[0]

    sys.stdout.write('FORMATTING GIG NAME...')
    try:
        gigParse = gig.split('/')
        if (len(gigParse) > 1):
            i = 1
            gigFileName = gigParse[0]
            while (i < (len(gigParse))):
                gigFileName = '%s-%s' % (gigFileName, gigParse[i])
                i += 1
        else:
            gigFileName = gigParse
    except:
        print("Error formatting gig.")
        return 0
    sys.stdout.write('\t[DONE]\n')

    gigFileName = gigFileName.split('\x0A')[0]
    gigFileName = gigFileName.split('\r')[0]
    print('GIG FILE NAME: %s' % (gigFileName))

    sys.stdout.write('Writing previous setlist...')
    try:
        previousText = open('text/previous', 'w')
        previousText.write(gig)
        previousText.close()
    except:
        print("Error writing setlist to previous")
        return 0

    try:
        previousText = open('text/previous', 'a')
    except:
        print("Error opening previous set to write")
        return 0

    i = 0
    while (i < len(setlist)):
        previousText.write(setlist[i])
        i += 1
    previousText.close()
    sys.stdout.write('\t[DONE]\n')
    sys.stdout.write('Previous setlist completed. Copying to archived file...')

    try:
        previousText = open('text/previous', 'r')
        previousList = previousText.readlines()
    except:
        print("Error opening previous set to copy")
        return 0

    try:    
        archivePath = os.path.abspath("%s%s" % (filepath, gigFileName))
        archiveText = open(archivePath, 'a')
    except:
        print("Error creating archive file")
        return 0

    i = 0
    while (i < len(previousList)):
        print('\tCopying: %s' % (previousList[i]))
        archiveText.write(previousList[i])
        i += 1

    archiveText.close()
    previousText.close()

    sys.stdout.write('\t[DONE]\n')
    outputString = 'Current setlist copied over as previous set.'
    return outputString

# Takes 2 songs, finds the first song in the set, replaces it with the second
# Returns 0 if there's an error
def replace_song(argument):
    errorCode = 0
    compared = 0
    songs = argument.split(', ')
    length = len(songs)
    outputString = ''

    if length != 2:
        errorCode = 1
    else:
        try:
            songText = open('text/setlist', 'r')
            setList = songText.readlines()
            length = len(setList)
        except:
            print("Error opening file for replace_song")
            return 0

        compareSong = songs[0]
        compareSong = acronym_replace(compareSong)

        replaceSong = songs[1]
        replaceSong = acronym_replace(replaceSong)

        setList = list(setList)

        print('Replacing %s with %s' % (compareSong, replaceSong))

        i = 0
        while i < length:
            currentSong = setList[i]
            currentSong = currentSong.split('\n')[0]
            if (currentSong == compareSong):
                setList[i] = replaceSong + '\n'
                compared = 1
                break
            i += 1

        setList = tuple(setList)
        songText.close()

        if (compared == 1):
            sys.stdout.write('Saving setlist...')
            songText = open('text/setlist', 'w')
            songText.write('')
            songText.close()

            songText = open('text/setlist', 'a')
            i = 0
            while i < length:
                songText.write(setList[i])
                i += 1
            songText.close()
            sys.stdout.write('\t[DONE]\n')

    if (errorCode == 1):
        print('Replace Error: Invalid argument count')
        outputString = 'ERROR: Invalid number of arguments.'
    else:
        if (compared == 0):
            print('Replace Error: Song not found')
            outputString = 'ERROR: Could not find the song to replace.'
        else:
            outputString = 'Song has been replaced.'

    return outputString

# Deletes a number of songs given in the argument
# Returns the number of succesfull song deletions, 0 if there's an error
def delete_song(argument):
    compared = 0
    deleteCount = 0
    deletePosition = 0
    ouputString = ''

    songs = argument.split(', ')
    songCount = len(songs)
    print('Deleting %d songs...' % (songCount))

    current = 0
    while (current < songCount):
        compared = 0

        compareSong = songs[current]
        compareSong = acronym_replace(compareSong)
        sys.stdout.write('Comparing song: %s' % (compareSong))

        try:
            songText = open('text/setlist', 'r')
            setlist = songText.readlines()
            length = len(setlist)
            songText.close()
        except:
            print("Error opening setlist file for delete_song")
            return 0

        i = 0
        while (i < length):
            setlist[i] = remove_newline_return(setlist[i])
            if (compareSong == setlist[i]):
                deletePosition = i
                compared = 1
                break
            i += 1

        if (compared == 1):
            try:
                songText = open('text/setlist', 'w')
                songText.write('')
                songText.close()

                songText = open('text/setlist', 'a')
            except:
                print("Error opening setlist file for delete_song")
                return 0            

            i = 0
            while (i < deletePosition):
                setlist[i] = "%s\n" % (setlist[i])
                songText.write(setlist[i])
                i += 1

            i = deletePosition + 1
            while (i < length):
                songText.write(setlist[i])
                i += 1

            songText.close()
            deleteCount += 1
            sys.stdout.write('\tDELETED')

        print('\n')
        current += 1

    print('Deleted %d/%d songs' % (deleteCount, songCount))
    if (deleteCount == 0):
        outputString = 'Could not delete any songs.'
    else:
        outputString = 'Deleted %d out of %d songs.' % (deleteCount, songCount)

    return outputString
