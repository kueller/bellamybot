myList = 'Hello', 'to', 'the', 'fucking', 'world'
text = open('newlist', 'w')
text.write('')
text.close()

length = len(myList)

i = 0
while i < length:
	if myList[i] == 'fucking':
		print(i)
		break
	i += 1



if i == length:
	print("Word not found.")
else:
	text = open('newlist', 'a')
	
	j = 0
	while j < i:
		text.write(myList[j] + '\n')
		j += 1
		
	j = i + 1
	while j < length:
		text.write(myList[j] + '\n')
		j += 1
		
	
