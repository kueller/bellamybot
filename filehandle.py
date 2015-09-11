# Remove newline and return characters from an entry
def remove_nr(string):
    string = string.split('\n')[0]
    string = string.split('\r')[0]
    return string

# Gets all the lines of a file and returns them as a list
# Throws IOError exception for any issues opening and closing the file
def get_list(filename):
    try:
        fileText = open(filename, 'r', encoding='utf-8')
        fileList = fileText.read().splitlines()
        fileText.close()
    except:
        raise IOError("Error opening " + filename)

    fileList = list(fileList)
    return fileList

# Recieves a list and writes each entry of the list as a line in a file
# Opens in write mode, so any contents in the file will be overwritten
# Throws an IOError exception for any issues opening and closing the file
def put_list(filename, fileList):
    fileList = tuple(fileList)

    try:
        fileText = open(filename, 'w', encoding='utf-8')
    except:
        raise IOError("Error opening " + filename)

    for entry in fileList:
        fileText.write(entry + '\n')

    fileText.close()

# Takes a string and appends it as a new line to a file
# Throws an IOError exception for any issues opening and closing the filexx
def list_append(filename, entry):
    try:
        fileText = open(filename, 'a', encoding='utf-8')
    except:
        raise IOError("Error opening " + filename)

    fileText.write(entry + '\n')
    fileText.close()

# Clears a file
# Throws an IOError exception for any issues opening the file
def clear_file(filename):
    try:
        fileText = open(filename, 'w', encoding='utf-8')
    except:
        raise IOError("Error opening " + filename)

    fileText.write('')
    fileText.close()
