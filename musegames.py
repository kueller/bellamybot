import sys
import socket
import txtfunctions
from random import randint

# Chooses a random closer from file (opener/closer) 
# See setlistgenerator.py for more info on files.
def random_game(filename):
	choice = randint(0,7)
	
	text = open(filename, 'r')
	options = text.readlines()
	
	randomResult = options[choice]
	randomResult = txtfunctions.remove_newline_return(randomResult)
	return randomResult

def T2L_roulette():
        spin = randint(0,10)
        if (spin <= 4):
                return 'The roulette landed on New Born!'
        elif (spin >= 5) and (spin <= 9):
                return 'The roulette landed on Stockholm Syndrome!'
        else:
                return 0

def roulette_green(nick):
        spin = randint(0,2)
        if (not(spin)):
                return ('Congratulations %s, you got Dead Star!' % (nick))
        elif (spin == 1):
                return ('Congratulations %s, you got Micro Cuts!' % (nick))
        else:
                return ('Congratulations %s, you got Unnatural Selection!'\
                                                                  % (nick))

# Manson game, gives or takes a 1-10 random number of Mansons to the user.
# Values stored offline and assigned to nick. Same nick can play continuously.
def manson_game(nick):
        outputStr = None
        
	mansonText = open('manson', 'r')
	mansonList = mansonText.readlines()	
	length = len(mansonList)	
	mansonText.close()
	
	nickExists = 0	
	
	mansonCount = randint(1,10)
	mansonAddDec = randint(0,1)	
	
	mansonRand = mansonCount
	
	if (mansonAddDec == 0):
		mansonCount = 0 - mansonCount	
	
	mansonList = list(mansonList)	
	
	i = 0
	while (i < length):
		currentEntry = mansonList[i]
		currentNick = currentEntry.split(':')[0]
		if (nick == currentNick):
			value = currentEntry.split(':')[1]
			value = value.split('\n')[0]
			value = int(value)
			
			mansonCount = mansonCount + value			
			mansonList[i] = "%s:%d\n" % (nick, mansonCount)
			
			mansonList = tuple(mansonList)
			
			mansonText = open('manson', 'w')
			mansonText.write('')
			mansonText.close()
			
			mansonText = open('manson', 'a')
				
			j = 0
			while (j < length):
				mansonText.write(mansonList[j])
				j += 1
			mansonText.close()
			
			nickExists = 1
			
			break			
		i += 1		
	
	if (nickExists == 0):
		currentString = nick + ':' + ("%d" % mansonCount) + '\n'
	
		mansonText = open('manson', 'a')
		mansonText.write(currentString)		
		mansonText.close()
	
	if (mansonAddDec == 0):		
		outputStr = "%s lost %d Mansons. Your total number of Mansons is now %d"\
					% (nick, mansonRand, mansonCount)
	
	elif (mansonAddDec == 1):		
		outputStr = ( "%s ganed %d Mansons. "\
                              "Your total number of Mansons is now %d"\
			      % (nick, mansonRand, mansonCount))
		
	return outputStr
