import random
import filehandle

# Random setlist is constructed in this class.
# Sets have a main set, and can have one or two encores.
# More info in setlistgenerator.py
class Setlist:
    
    openers = None
    songs = None
    piano = None
    setClosers = None
    gigClosers = None

    mainSet = None
    firstEncore = None
    secondEncore = None

    # Initialization gets the file list for each text file.
    # Throws Exception on I/O errors.
    def __init__(self):
        try:
            self.openers = filehandle.get_list('text/opener')
            self.songs = filehandle.get_list('text/songs')
            self.piano = filehandle.get_list('text/piano')
            self.setClosers = filehandle.get_list('text/setcloser')
            self.gigClosers = filehandle.get_list('text/gigcloser')
        except IOError as e:
            raise IOError(e)

        self.mainSet = []
        self.firstEncore = []
        self.secondEncore = []

    # Will append a list (of number "length") of unique songs to the
    # list defined by "section" from the list defined by "songList"
    def constructor(self, section, songList, length):
        for i in range(0, length):
            songEntry = random.choice(songList)
            while ((songEntry in self.mainSet)
                   or (songEntry in self.firstEncore)
                   or (songEntry in self.secondEncore)):
                songEntry = random.choice(songList)
                
            section.append(songEntry)            

    # Chunky constructor setlists that simply call constructor to make
    # different parts of the random setlist.
    # Again, see setlistgenerator.py for set structure info.
    def constructMainSet(self):
        self.constructor(self.mainSet, self.openers, 1)
        self.constructor(self.mainSet, self.songs, random.randint(5,7))
        self.constructor(self.mainSet, self.piano, random.randint(1,3))
        self.constructor(self.mainSet, self.songs, random.randint(6,7))
        self.constructor(self.mainSet, self.setClosers, 1)

    def constructSingleEncore(self):
        self.constructor(self.firstEncore, self.openers, 1)
        self.constructor(self.firstEncore, self.songs, 1)
        self.constructor(self.firstEncore, self.gigClosers, 1)

    def constructTwoEncore(self):
        self.constructor(self.firstEncore, self.openers, 1)
        self.constructor(self.firstEncore, self.songs, random.randint(1,2))
        self.constructor(self.firstEncore, self.setClosers, 1)

        self.constructor(self.secondEncore, self.openers, 1)
        self.constructor(self.secondEncore, self.songs, 1)
        self.constructor(self.secondEncore, self.gigClosers, 1)

    # Goes through the lists and creates one string for each
    # Returns a dictionary containing the 3 possible parts of the setlist
    def printSet(self):
        randomSet = {
            'setlist': None,
            'encore1': None,
            'encore2': None
        }

        for song in self.mainSet:
            if randomSet['setlist'] == None:
                randomSet['setlist'] = song
            else:
                randomSet['setlist'] = "%s, %s" % (randomSet['setlist'], song)

        if len(self.secondEncore) == 0:
            randomSet['encore1'] = "ENCORE: "
            for song in self.firstEncore:
                if randomSet['encore1'] == "ENCORE: ":
                    randomSet['encore1'] = "%s%s" % (randomSet['encore1'], song)
                else:
                    randomSet['encore1'] = "%s, %s" % (randomSet['encore1'], song)
        else:
            randomSet['encore1'] = "ENCORE 1: "
            randomSet['encore2'] = "ENCORE 2: "

            for song in self.firstEncore:
                if randomSet['encore1'] == "ENCORE 1: ":
                    randomSet['encore1'] = "%s%s" % (randomSet['encore1'], song)
                else:
                    randomSet['encore1'] = "%s, %s" % (randomSet['encore1'], song)

            for song in self.secondEncore:
                if randomSet['encore2'] == "ENCORE 2: ":
                    randomSet['encore2'] = "%s%s" % (randomSet['encore2'], song)
                else:
                    randomSet['encore2'] = "%s, %s" % (randomSet['encore2'], song)

        return randomSet
