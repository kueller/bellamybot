import sys
import txtfunctions
from random import randint

# Setlist generator
# 77 songs 				"songs"
# 8 openers				"opener"
# 15 piano songs		"piano"
# 15 set closers		"setcloser"
# 8 gig closers			"gigcloser"

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

randomSet = None
encoreOne = ''
encoreTwo = ''
finalSet = None

MAINSET = 1
ENCORE1 = 2
ENCORE2 = 3

def set_construct(length, array, randlimit, settype):
	global randomSet
	global encoreOne
	global encoreTwo
	
	if(settype == MAINSET):
		i = 0		
		while i < length:
			songLine = randint(0, randlimit)
			songEntry = array[songLine]
			songEntry = txtfunctions.remove_newline_return(songEntry)
			while songEntry in randomSet:
				songLine = randint(0, randlimit)
				songEntry = array[songLine]
				songEntry = txtfunctions.remove_newline_return(songEntry)
			randomSet = '%s, %s' % (randomSet, songEntry)
			i += 1
			
	elif(settype == ENCORE1):
		songLine = randint(0,randlimit)
		songEntry = array[songLine]
		songEntry = txtfunctions.remove_newline_return(songEntry)
		while (songEntry in randomSet) or (songEntry in encoreOne):
			songLine = randint(0,randlimit)
			songEntry = array[songLine]
			songEntry = txtfunctions.remove_newline_return(songEntry)
		encoreOne = '%s, %s' % (encoreOne, songEntry)
		
	elif(settype == ENCORE2):		
		songLine = randint(0,randlimit)
		songEntry = array[songLine]
		songEntry = txtfunctions.remove_newline_return(songEntry)
		while ((songEntry in randomSet) or (songEntry in encoreOne) or 
				(songEntry in encoreTwo)):
			songLine = randint(0,randlimit)
			songEntry = array[songLine]
			songEntry = txtfunctions.remove_newline_return(songEntry)
		encoreTwo = '%s, %s' % (encoreTwo, songEntry)


def generate():
	firstSetLength = randint(5,7)
	pianoLength = randint(1,3)
	secondSetLength = randint(6,7)
	encoreCount = randint(1,2)
	
	print('CREATING SETLIST...')
	print('\tFirst length: %d' % (firstSetLength))
	print('\tPiano length: %d' % (pianoLength))
	print('\tSecond length: %d' % (secondSetLength))
	print('\tNumber of encores: %d' % (encoreCount))	
	
	global randomSet
	global finalSet
	global encoreOne
	global encoreTwo
	
	openers = open('opener', 'r')
	openerArray = openers.readlines()
	
	songs = open('songs', 'r')
	songsArray = songs.readlines()
	
	pianos = open('piano', 'r')
	pianoArray = pianos.readlines()
	
	setcloser = open('setcloser', 'r')
	setcloserArray = setcloser.readlines()
	
	gigcloser = open('gigcloser', 'r')
	gigcloserArray = gigcloser.readlines()
	
	# Create the gig opener
	songLine = randint(0,7)
	
	songEntry = openerArray[songLine]
	songEntry = txtfunctions.remove_newline_return(songEntry)
	randomSet = songEntry	
	
	sys.stdout.write('First section...  \t')
        set_construct(firstSetLength, songsArray, 76, MAINSET)	
	sys.stdout.write('[DONE]\n')	
	
	sys.stdout.write('Piano section...  \t')
        set_construct(pianoLength, pianoArray, 14, MAINSET)	
	sys.stdout.write('[DONE]\n')	
	
	sys.stdout.write('Second section... \t')
        set_construct(secondSetLength, songsArray, 76, MAINSET)
	sys.stdout.write('[DONE]\n')
	
	sys.stdout.write('Closing main set...\t')
        set_construct(1, setcloserArray, 14, MAINSET)	
	sys.stdout.write('[DONE]\n')
	
	set_construct(1, openerArray, 7, ENCORE1)
	print('Beginning first encore...')	
	
	set_construct(1, songsArray, 76, ENCORE1)		
	
	if encoreCount == 1:
		set_construct(1, gigcloserArray, 7, ENCORE1)		
		finalSet = randomSet, encoreOne
		print('Encore 1 of 1 complete...')	
	
	elif encoreCount == 2:
		set_construct(1, setcloserArray, 14, ENCORE1)		
		print('Encore 1 of 2 complete...')
		
		set_construct(1, openerArray, 7, ENCORE2)		
		set_construct(1, songsArray, 76, ENCORE2)		
		set_construct(1, gigcloserArray, 7, ENCORE2)
		finalSet = randomSet, encoreOne, encoreTwo
		print('Encore 2 of 2 complete...')	
	
	openers.close()
	songs.close()
	pianos.close()
	setcloser.close()
	gigcloser.close()
	
	print('Setlist completed')
	return finalSet
