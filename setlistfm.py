import json
import random
import requests

url1 = "http://api.setlist.fm/rest/0.1/artist/"
url2 = "http://api.setlist.fm/rest/0.1/setlist/version/"

waaiURL = "http://api.waa.ai/shorten?url="

# Shortens a given URL using the API from http://waa.ai
def url_shorten(url):
    r = requests.get("%s%s" % (waaiURL, url))
    data = r.json()

    return(data['data']['url'])

# Using the setlist.fm API, gets a random setlist from a random search page
# and formats it into a list of messages to be printed out.
# URL to setlist page is shortened using url_shorten
# Takes the artist's mbid as an input
def get_setlist(mbid):
    output = []

    # I really don't know how many pages there are but this seems to work.
    pageNo = random.randint(1,50)

    # Get a list of search results from page pageNo
    url = "%s%s/setlists.json?p=%d" % (url1, mbid, pageNo)

    r = requests.get(url)
    data = r.json()
        
    setlists = data['setlists']['setlist']
    randomSet = random.choice(setlists)
    setID = randomSet['@versionId']

    print("Generating setlist from " + randomSet['url'])
    
    # Get the data from that specific setlist chosen
    s = requests.get(url2 + setID + ".json")
    setlistData = s.json()

    output.append('')

    # Format the gig in the same way all BellamyBot gigs are
    output[0] = setlistData['setlist']['@eventDate']
    output[0] = ("%s - %s, %s, %s:"
                 % (output[0],
                    setlistData['setlist']['venue']['@name'],
                    setlistData['setlist']['venue']['city']['@name'],
                    setlistData['setlist']['venue']['city']['country']['@code']))

    try:
        setlist = setlistData['setlist']['sets']['set']
    except TypeError:
        output.append("This setlist appears to be emtpy.")
        output.append("Link: %s" % url_shorten(randomSet['url']))
        return output

    # The tendency for the json setlist results to alternate between
    # lists and dictionaries depending on whether a section has more than one
    # song results in this really messy multi-indented block of code.
    i = 1
    if isinstance(setlist, list):
        for chunks in setlist:
            output.append('')
            songs = chunks['song']
            if isinstance(songs, list):
                for song in songs:
                    if output[i] == '':
                        output[i] = song['@name']
                    else:
                        output[i] = "%s, %s" % (output[i], song['@name'])
            elif isinstance(songs, dict):
                output[i] = songs['@name']
            i = i + 1
    elif isinstance(setlist, dict):
        output.append('')
        songs = setlist['song']
        if isinstance(songs, list):
            for song in songs:
                if output[i] == '':
                    output[i] = song['@name']
                else:
                    output[i] = "%s, %s" % (output[i], song['@name'])
        elif isinstance(songs, dict):
            output[i] = songs['@name']

    output.append("Link: %s" % url_shorten(randomSet['url']))
    return output
