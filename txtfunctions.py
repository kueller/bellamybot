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
        entry = 'Stockholm Syndrome'
    elif entry == 'TaB':
        entry = 'Take A Bow'
    elif entry == 'TIRO':
        entry = 'Time Is Running Out'
    elif entry == 'TOADA':
        entry = 'Thoughts of a Dying Atheist'
    return entry

# Adds a song, or string of songs, to the .setlist file
# I/O Exceptions are silently ignored.
def add_song(argument):
    songList = argument.split(', ')

    for song in songList:
        song = acronym_replace(song)
        try:
            filehandle.list_append('text/setlist', song)
        except IOError:
            print("Error adding song to setlist")

# Removed the most recently entered song from the setlist file
# Passes on I/O exceptions
# Throws Index exception is called on an empty setlist
def song_undo():
    try:
        undoList = filehandle.get_list('text/setlist')
    except IOError:
        raise IOError("Error opening file for song_undo")
    
    if len(undoList) != 0:
        del undoList[len(undoList) - 1]
    else:
        raise IndexError("Empty setlist")

    try:
        filehandle.put_list('text/setlist', undoList)
    except IOError:
        raise IOError("Error rewriting list for song_undo")
    return

# Prints any setlest fed into it and returns a string to be messaged
# Very slow. Will fix in the future.
# Passes on I/O Exceptions
def print_set(filename):
    try:
        fileList = filehandle.get_list(filename)
    except IOError:
        raise IOError("Error opening file to print")
    
    fileSize = len(fileList)

    if fileSize == 0:
        print('EMPTY SETLIST')
        listFinal = ''
    else:
        currentSong = fileList[0]
        currentSong = filehandle.remove_nr(currentSong)
        listFinal = currentSong

        # Extra formatting to print "previous setlist"
        if filename == 'text/previous':
            print('Printing PREVIOUS')
            listFinal = '%s: ' % (currentSong)

            currentSong = fileList[1]
            currentSong = filehandle.remove_nr(currentSong)
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
# Passes on I/O Exceptions
# Throws RuntimeError exception for gig formatting issues.
def set_previous():
    setlist = filehandle.get_list('text/setlist')
    gig = filehandle.get_list('text/gig')

    print('GIG: %s' % (gig))

    if len(gig) == 0:
        print('SetPrevious Error: GIG not found')
        outputString = 'ERROR: No gig set.'
        return outputString
    if len(setlist) == 0:
        print('SetPrevious Error: Empty setlist')
        outputString = 'ERROR: Setlist is empty.'
        return outputString

    gig = gig[0]

    sys.stdout.write('FORMATTING GIG NAME...')
    try:
        gigParse = gig.split('/')
        if len(gigParse) > 1:
            i = 1
            gigFileName = gigParse[0]
            while i < len(gigParse):
                gigFileName = '%s-%s' % (gigFileName, gigParse[i])
                i += 1
        else:
            gigFileName = gigParse[0]
    except:
        raise RuntimeError("Error formatting gig")
    sys.stdout.write('\t[DONE]\n')

    gigFileName = gigFileName.split('\x0A')[0]
    gigFileName = gigFileName.split('\r')[0]
    print('GIG FILE NAME: %s' % (gigFileName))

    sys.stdout.write('Writing previous setlist...')

    archivePath = "GigArchive/" + gigFileName

    gig = [gig]

    try:
        filehandle.put_list('text/previous', gig)
        filehandle.put_list(archivePath, gig)
    except IOError:
        raise IOError("Error writing setlists for set_previous")

    for entry in setlist:
        try:
            filehandle.list_append('text/previous', entry)
            filehandle.list_append(archivePath, entry)
        except IOError:
            raise IOError("Error appending song for set_previous")

    sys.stdout.write('\t[DONE]\n')

    outputString = 'Current setlist copied over as previous set.'
    return outputString

# Takes 2 songs, finds the first song in the set, replaces it with the second
# Passes on I/O Exceptions
# Most other errors will be returned in outputMsg to be sent through IRC.
def replace_song(argument):
    compared = False
    songs = argument.split(', ')
    length = len(songs)

    if length != 2:
        print("Invalid replacement arguments")
        outputMsg = "ERROR: Invalid number of arguments."
        return outputMsg
    else:
        try:
            setlist = filehandle.get_list('text/setlist')
        except IOError:
            raise IOError("Error getting setlist for replace_song")
        
        compareSong = songs[0]
        compareSong = acronym_replace(compareSong)

        replaceSong = songs[1]
        replaceSong = acronym_replace(replaceSong)

        sys.stdout.write('Replacing %s with %s' % (compareSong, replaceSong))

        try:
            songIndex = setlist.index(compareSong)
            setlist[songIndex] = replaceSong
            compared = True
        except:
            print('Replace Error: Song not found')
            outputMsg = "ERROR: Could not find the song to replace."
            return outputMsg

        if compared:
            try:
                filehandle.put_list('text/setlist', setlist)
            except IOError:
                raise IOError("Error writing set for replace_song")
            sys.stdout.write('\t[DONE]\n')

    outputMsg = "Song has been replaced"
    return outputMsg

# Nearly identical to replace_song. I will fix that some day
# Takes two songs, finds if the first song is in the set
# and inserts the second song before it
def insert_song(argument):
    compared = False
    songs = argument.split(', ')
    length = len(songs)

    if length != 2:
        print("Invalid replacement arguments")
        outputMsg = "ERROR: Invalid number of arguments."
        return outputMsg
    else:
        try:
            setlist = filehandle.get_list('text/setlist')
        except IOError:
            raise IOError("Error getting setlist for insert_song")
        
        insertSong = songs[0]
        insertSong = acronym_replace(insertSong)

        compareSong = songs[1]
        compareSong = acronym_replace(compareSong)

        sys.stdout.write('Inserting %s before %s' % (insertSong, compareSong))

        try:
            songIndex = setlist.index(compareSong)
            setlist.insert(songIndex, insertSong)
            compared = True
        except:
            print('Compare Error: Song not found')
            outputMsg = "ERROR: Could not find the song to insert before."
            return outputMsg

        if compared:
            try:
                filehandle.put_list('text/setlist', setlist)
            except IOError:
                raise IOError("Error writing set for insert_song")
            sys.stdout.write('\t[DONE]\n')
        
        outputMsg = ("Inserted %s before %s" % (insertSong, compareSong))
        return outputMsg

# Deletes a number of songs given in the argument
# Returns a string to be sent to IRC conatining the number
# of successful deletions.
# Passes on I/O Exceptions
def delete_song(argument):
    compared = False
    deleteCount = 0

    songs = argument.split(', ')
    songCount = len(songs)
    print('Deleting %d songs...' % (songCount))

    for song in songs:
        compared = False

        song = acronym_replace(song)
        sys.stdout.write('Comparing song: %s' % (song))

        try:
            setlist = filehandle.get_list('text/setlist')
        except IOError:
            raise IOError("Error getting set for delete_song")
        
        try:
            songIndex = setlist.index(song)
            compared = True
        except:
            None

        if compared:
            try:
                setlist.remove(song)
                deleteCount = deleteCount + 1
            except:
                print("Error deleting song")
            
            try:
                filehandle.put_list('text/setlist', setlist)
            except IOError:
                raise IOError("Error writing set for delete_song")

            sys.stdout.write('\tDELETED')

        print('\n')
 
    print('Deleted %d/%d songs' % (deleteCount, songCount))

    if (deleteCount == 0):
        outputMsg = 'Could not delete any songs.'
    else:
        outputMsg = 'Deleted %d out of %d songs.' % (deleteCount, songCount)

    return outputMsg
