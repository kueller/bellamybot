import filehandle

UNDOLIST = []
INDEX = 0

SETFILE  = 'text/setlist'

# Initializes, or re-initializes, the UNDOLIST to be only the current selist.
def refresh():
    global INDEX
    global UNDOLIST
    
    UNDOLIST = [] 
    try:
        setlist = filehandle.get_list(SETFILE)
    except IOError as i:
        print(i)

    UNDOLIST.append(setlist)
    INDEX = 0

# Appends a state to the undo list.
# If a new state is added and the index is not pointing to the last value
# (i.e. undo was called) the new state will be inserted and will be the
# new end of the list. Other states will be removed.
def add():
    global INDEX
    global UNDOLIST

    try:
        setlist = filehandle.get_list(SETFILE)
    except IOError as i:
        print(i)

    if INDEX == len(UNDOLIST) - 1:
        UNDOLIST.append(setlist)
    elif INDEX < len(UNDOLIST) - 1:
        UNDOLIST[INDEX + 1] = setlist
        UNDOLIST = UNDOLIST[0:INDEX + 2]

    INDEX += 1

# Decrements the index and writes the previous state setlist as the current.
def undo():
    global INDEX
    global UNDOLIST

    if INDEX == 0:
        return False
    
    setlist = UNDOLIST[INDEX - 1]

    try:
        filehandle.put_list(SETFILE, setlist)
    except IOError as i:
        print(i)
        return False

    INDEX -= 1
    return True

# Increments the index and writes the following state setlist as the current.
def redo():
    global INDEX
    global UNDOLIST

    if INDEX >= len(UNDOLIST) - 1:
        return False

    setlist = UNDOLIST[INDEX + 1]

    try:
        filehandle.put_list(SETFILE, setlist)
    except IOError as i:
        print(i)
        return False

    INDEX += 1
    return True
        
    
