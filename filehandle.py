# Remove newline and return characters from an entry
def remove_nr(string):
    string = string.split('\n')[0]
    string = string.split('\r')[0]
    return string


def get_list(filename):
    try:
        fileText = open(filename, 'r')
        fileList = fileText.read().splitlines()
        fileText.close()
    except:
        print("Error opening " + filename)
        return -1

    fileList = list(fileList)

    return fileList

def put_list(filename, fileList):
    fileList = tuple(fileList)

    try:
        fileText = open(filename, 'w')
    except:
        print("Error opening " + filename)
        return -1

    for entry in fileList:
        fileText.write(entry + '\n')

    fileText.close()

    return 1

def list_append(filename, entry):
    try:
        fileText = open(filename, 'a')
    except:
        print("Error opening " + filename)
        return -1

    fileText.write(entry)
    fileText.close()
    return 1
        
        
