import sys
import filehandle

# Allows for replacement of acronym entries
def acronym_replace(entry):
    entry = filehandle.remove_nr(entry)
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
    elif entry == 'SS':
        entry == 'Stockholm Syndrome'
    elif entry == 'TaB':
        entry = 'Take A Bow'
    elif entry == 'TIRO':
        entry = 'Time Is Running Out'
    elif entry == 'TOADA':
        entry = 'Thoughts of a Dying Atheist'
    return entry

# Adds a song, or string of songs, to the .setlist file
# Returns 0 if there's an error
def add_song(argument):
    songList = argument.split(', ')
    songCount = len(songList)
    
    if (songCount == 1):
        songList[0] = acronym_replace(songList[0])
        err = filehandle.list_append('text/setlist', '%s\n' % songList[0])
        if (err == -1):
            return -1
    else:
        for song in songList:
            song = acronym_replace(song)
            err = filehandle.list_append('text/setlist', song + '\n')

    return 1

# Removed the most recently entered song from the .setlist file
# Returns 0 if there's an error
def song_undo():
    undoList = filehandle.get_list('text/setlist')
    if (undoList == -1):
        return -1

    del undoList[len(undoList) - 1]

    err = filehandle.put_list('text/setlist', undoList)
    if (err == -1):
        return -1

    return 1

# Prints any setlest fed into it and returns a string to be messaged
# Returns -1 if there's an error (Note: only function to not return error 0)
def print_set(filename):
    fileList = filehandle.get_list(filename)
    fileSize = len(fileList)

    if (fileSize == 0):
        print('EMPTY SETLIST')
        listFinal = ''
    else:
        currentSong = fileList[0]
        currentSong = filehandle.remove_nr(currentSong)
        listFinal = currentSong

        # Extra formatting to print "previous setlist"
        if (filename == 'previous'):
            print('Printing PREVIOUS')
            listFinal = '%s: ' % (currentSong)

            currentSong = fileList[1]
            currentSong = filehandle_remove_nr(currentSong)
            listFinal = '%s%s' % (listFinal, currentSong)

            i = 2
            while i < fileSize:
                currentSong = fileList[i]
                currentSong = filehandle.remove_nr(currentSong)
                listFinal = '%s, %s' % (listFinal, currentSong)
                i += 1

        else:
            print('Printing set')
            i = 1
            while i < fileSize:
                currentSong = fileList[i]
                currentSong = filehandle.remove_nr(currentSong)
                listFinal = '%s, %s' % (listFinal, currentSong)
                i += 1

    return listFinal

# Copies the gig and setlist to a previous setlist file
# Then copies the previous setlist to an archive with the gig as the file name
# Returns 0 if there's an error
def set_previous():
    setlist = filehandle.get_list('text/setlist')
    gig = filehandle.get_list('text/gig')

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
        return -1
    sys.stdout.write('\t[DONE]\n')

    gigFileName = gigFileName.split('\x0A')[0]
    gigFileName = gigFileName.split('\r')[0]
    print('GIG FILE NAME: %s' % (gigFileName))

    sys.stdout.write('Writing previous setlist...')

    gig = [gig]
    err = filehandle.put_list('text/previous', gig)
    if (err == -1):
        return -1

    for entry in setlist:
        err = filehandle.list_append('text/previous', entry)
        if (err == -1):
            return -1

    sys.stdout.write('\t[DONE]\n')
    sys.stdout.write('Previous setlist completed. Copying to archived file...')

    previousList = filehandle.get_list('text/previous')
    if (err == -1):
        return -1

    archivePath = "GigArchive/" + gigFileName
    err = filehandle.put_list(archivePath, previousList)
    if (err == -1):
        return -1

    sys.stdout.write('\t[DONE]\n')
    outputString = 'Current setlist copied over as previous set.'
    return outputString

# Takes 2 songs, finds the first song in the set, replaces it with the second
# Returns 0 if there's an error
def replace_song(argument):
    compared = 0
    songs = argument.split(', ')
    length = len(songs)

    if length != 2:
        print("Invalid replacement arguments")
        outputString = "ERROR: Invalid number of arguments."
        return outputString
    else:
        setlist = filehandle.get_list('text/setlist')
        if (setlist == -1):
            return -1
        
        for entry in setlist:
            entry = entry.split('\n')[0]

        compareSong = songs[0]
        compareSong = acronym_replace(compareSong)

        replaceSong = songs[1]
        replaceSong = acronym_replace(replaceSong)

        print('Replacing %s with %s' % (compareSong, replaceSong))

        try:
            songIndex = setlist.index(compareSong)
            setlist[songIndex] = replaceSong
            compared = 1
        except:
            print('Replace Error: Song not found')
            outputString = "ERROR: Could not find the song to replace."
            return outputString

        if (compared == 1):
            err = filehandle.put_list('text/setlist', setlist)
            if (err == -1):
                return -1
            sys.stdout.write('\t[DONE]\n')

    outputString = "Song has been replaced"
    return outputString


# Deletes a number of songs given in the argument
# Returns the number of succesfull song deletions, 0 if there's an error
def delete_song(argument):
    compared = 0
    deleteCount = 0

    songs = argument.split(', ')
    songCount = len(songs)
    print('Deleting %d songs...' % (songCount))

    for song in songs:
        compared = 0

        song = acronym_replace(song)
        sys.stdout.write('Comparing song: %s' % (song))

        setlist = filehandle.get_list('text/setlist')
        if (setlist == -1):
            return -1

        try:
            songIndex = setlist.index(song)
            compared = 1
        except:
            None

        if (compared == 1):
            try:
                setlist.remove(song)
                deleteCount = deleteCount + 1
            except:
                print("Error deleting song")
            
            err = filehandle.put_list('text/setlist', setlist)
            if (err == -1):
                 return -1

            sys.stdout.write('\tDELETED')

        print('\n')
 
    print('Deleted %d/%d songs' % (deleteCount, songCount))

    if (deleteCount == 0):
        outputString = 'Could not delete any songs.'
    else:
        outputString = 'Deleted %d out of %d songs.' % (deleteCount, songCount)

    return outputString
    
