import txtfunctions
from random import randint

def crowd_choice():
	crowdText = open('crowd', 'r')
	crowdList = crowdText.readlines()
	crowdLength = len(crowdList)
	crowdText.close()
	
	if (crowdLength > 0):
		choice = randint(0, crowdLength)
		songChoice = crowdList[choice]
		songChoice = songChoice.split('\n')[0]		
		
		outputString = "I have decided to play %s" % (songChoice)
	
	else:
		outputString = "No one gave suggestions so I'll play Guiding Light "\
						"instead."		
	
	crowdText = open('crowd', 'w')
	crowdText.write('')
	crowdText.close()
	
	return outputString	

#Says a random phrase from ".botphrases"
def random_phrase():
	randomText = open('botphrases', 'r')
	randomList = randomText.readlines()
	phraseLength = len(randomList)
	randomText.close()
	throw = randint(1,3)
	
	if (throw != 3):
		line = randint(0, phraseLength - 1)		
		phrase = randomList[line]
		phrase = phrase.split('\n')[0]
	else:
		phrase = '\x01ACTION throws %d Musos into the air' % randint(2,20)
	
	return phrase		
