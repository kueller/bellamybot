import filehandle
from random import randint

# Random setlist is constructed in this class.
# Sets have a main set, and can have one or two encored.
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
            songLine = randint(0, len(songList) - 1)
            songEntry = songList[songLine]
            while ((songEntry in self.mainSet)
                   or (songEntry in self.firstEncore)
                   or (songEntry in self.secondEncore)):
                songLine = randint(0, len(songList) - 1)
                songEntry = songList[songLine]
                
            section.append(songEntry)            
        
    def constructMainSet(self):
        self.constructor(self.mainSet, self.openers, 1)
        self.constructor(self.mainSet, self.songs, randint(5,7))
        self.constructor(self.mainSet, self.piano, randint(1,3))
        self.constructor(self.mainSet, self.songs, randint(6,7))
        self.constructor(self.mainSet, self.setClosers, 1)

    def constructSingleEncore(self):
        self.constructor(self.firstEncore, self.openers, 1)
        self.constructor(self.firstEncore, self.songs, 1)
        self.constructor(self.firstEncore, self.gigClosers, 1)

    def constructTwoEncore(self):
        self.constructor(self.firstEncore, self.openers, 1)
        self.constructor(self.firstEncore, self.songs, randint(1,2))
        self.constructor(self.firstEncore, self.setClosers, 1)

        self.constructor(self.secondEncore, self.openers, 1)
        self.constructor(self.secondEncore, self.songs, 1)
        self.constructor(self.secondEncore, self.gigClosers, 1)

    # Goes through the lists and creates one string for each
    # They are then messages through IRC. Requires the irc object to be
    # passed as an argument
    def printSet(self, irc):
        setlist = None
        encore1 = None
        encore2 = None
        for song in self.mainSet:
            if setlist == None:
                setlist = song
            else:
                setlist = "%s, %s" % (setlist, song)
        irc.msg("%s" % setlist)

        if len(self.secondEncore) == 0:
            encore1 = "ENCORE: "
            for song in self.firstEncore:
                if encore1 == "ENCORE: ":
                    encore1 = "%s%s" % (encore1, song)
                else:
                    encore1 = "%s, %s" % (encore1, song)
            irc.msg("%s" % encore1)
        else:
            encore1 = "ENCORE 1: "
            encore2 = "ENCORE 2: "
            for song in self.firstEncore:
                if encore1 == "ENCORE 1: ":
                    encore1 = "%s%s" % (encore1, song)
                else:
                    encore1 = "%s, %s" % (encore1, song)
            irc.msg("%s" % encore1)

            for song in self.secondEncore:
                if encore2 == "ENCORE 2: ":
                    encore2 = "%s%s" % (encore2, song)
                else:
                    encore2 = "%s, %s" % (encore2, song)
            irc.msg("%s" % encore2)
