import random
import filehandle

# Chooses a random closer from file (opener/closer) 
# See setlistgenerator.py for more info on files.
# Passes on the IOError exception if file could not be opened
def random_game(filename):
    try:
        options = filehandle.get_list(filename)
    except IOError:
        raise IOError("Could not open file for random_game")

    randomResult = random.choice(options)
    randomResult = filehandle.remove_nr(randomResult)
    return randomResult

# Lands on either New Born, Stockholm, or green
# Green is denoted by -1
def T2L_roulette():
    spin = random.randint(0,10)
    if spin <= 4:
        return "The roulette landed on New Born!"
    elif (spin >= 5) and (spin <= 9):
        return "The roulette landed on Stockholm Syndrome!"
    else:
        return -1

# Chooses a rarity if the roulette lands on green
def roulette_green(nick):
    spin = random.randint(0,2)
    if not(spin):
        return "Congratulations %s, you got Dead Star!" % (nick)
    elif spin == 1:
        return "Congratulations %s, you got Micro Cuts!" % (nick)
    else:
        return "Congratulations %s, you got Unnatural Selection!" % (nick)

# Manson game, gives or takes a 1-10 random number of Mansons to the user.
# Values stored offline and assigned to nick. Same nick can play continuously.
# Passes on IOError exception for any issues handling the text file
# Throws IndexError exception for issues finding the nick index or appending
def manson_game(nick):
    try:
        mansonList = filehandle.get_list('text/manson')
    except IOError:
        raise IOError("Could not open file for manson_game")

    nickExists = False

    mansonRand = random.randint(1,10)

    # True/False, whether or not Mansons will be added or removed
    mansonAddDec = random.randint(0,1) 

    for entry in mansonList:
        currentNick = entry.split(':')[0]
        if nick == currentNick:
            try:
                nickPosition = mansonList.index(entry)
            except:
                raise IndexError("Error getting index from manson list")
            nickExists = True

    if mansonAddDec == 0:
        mansonCount = 0 - mansonRand
    else:
        mansonCount = mansonRand

    if nickExists:
        value = mansonList[nickPosition].split(':')[1]
        value = int(value)

        mansonCount = value + mansonCount
        mansonList[nickPosition] = "%s:%d" % (nick, mansonCount)
    else:
        try:
            mansonList.append("%s:%d" % (nick, mansonCount))
        except:
            raise IndexError("Error appending new manson entry")

    mansonList = sorted(mansonList, key=str.lower)

    try:
        filehandle.put_list('text/manson', mansonList)
    except IOError:
        raise IOError("Error writing manson list")
    
    if mansonAddDec == 0:             
        return ("%s lost %d Mansons. Your total number of Mansons is now %d"
                     % (nick, mansonRand, mansonCount))

    elif mansonAddDec == 1:           
        return ("%s ganed %d Mansons. Your total number of Mansons is now %d"
                      % (nick, mansonRand, mansonCount))
