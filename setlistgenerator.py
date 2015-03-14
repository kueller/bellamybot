import random
from filehandle import get_list
from txtfunctions import create_set_string

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

# randomset: {'main', 'encore1', 'encore2'}

def set_constructor(section, songList, randomset, length):
    if length == 0:
        return

    songEntry = random.choice(songList)
    while ((songEntry in randomset['main'])
           or (songEntry in randomset['encore1'])
           or (songEntry in randomset['encore2'])):
        songEntry = random.choice(songList)

    section.append(songEntry)
    set_constructor(section, songList, randomset, length - 1)

def construct_main_set(randomset, openers, songs, piano, setclosers):
    set_constructor(randomset['main'], openers, randomset, 1);
    set_constructor(randomset['main'], songs,   randomset, random.randint(5,7))
    set_constructor(randomset['main'], piano,   randomset, random.randint(1,3))
    set_constructor(randomset['main'], songs,   randomset, random.randint(6,7))
    set_constructor(randomset['main'], setclosers, randomset, 1)

def construct_single_encore(randomset, openers, songs, closers):
    set_constructor(randomset['encore1'], openers, randomset, 1)
    set_constructor(randomset['encore1'], songs,   randomset, 1)
    set_constructor(randomset['encore1'], closers, randomset, 1)

def construct_double_encore(randomset, openers, songs, setclosers, gigclosers):
    construct_single_encore(randomset, openers, songs, setclosers)

    set_constructor(randomset['encore2'], openers,    randomset, 1)
    set_constructor(randomset['encore2'], songs,      randomset, 1)
    set_constructor(randomset['encore2'], gigclosers, randomset, 1)

def generate(irc):
    try:
        openers    = get_list('text/opener')
        songs      = get_list('text/songs')
        piano      = get_list('text/piano')
        setclosers = get_list('text/setcloser')
        gigclosers = get_list('text/gigcloser')
    except IOError as e:
        print(e)

    randomset = {
        'main':    [],
        'encore1': [],
        'encore2': []
    }

    encorecount = random.randint(0, 1)

    construct_main_set(randomset, openers, songs, piano, setclosers)
    irc.msg(create_set_string(randomset['main']))

    if encorecount == 0:
        construct_single_encore(randomset, openers, songs, gigclosers)
        irc.msg("ENCORE: " + create_set_string(randomset['encore1']))
    else:
        construct_double_encore(randomset, openers, songs, setclosers, gigclosers)
        irc.msg("ENCORE 1: " + create_set_string(randomset['encore1']))
        irc.msg("ENCORE 2: " + create_set_string(randomset['encore2']))
