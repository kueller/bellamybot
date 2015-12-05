import tweepy
import filehandle
from setlistfm import url_shorten

# Reads the keys from text/twitter and generates a tweepy API object.
def authorize_new_twit(filename):
    print("Authorizing twitter account from file.")
    
    CONSUMER_KEY = ''
    CONSUMER_KEY_SECRET = ''
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''
    
    text = filehandle.get_list(filename)
    for line in text:
        splitLine = line.split('=')
        if len(splitLine) < 2:
            continue
        arg   = splitLine[0].strip()
        value = splitLine[1].strip()

        if arg == "CONSUMER_KEY":
            CONSUMER_KEY = value
        elif arg == "CONSUMER_KEY_SECRET":
            CONSUMER_KEY_SECRET = value
        elif arg == "ACCESS_TOKEN":
            ACCESS_TOKEN = value
        elif arg == "ACCESS_TOKEN_SECRET":
            ACCESS_TOKEN_SECRET = value

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    twit = tweepy.API(auth)
    return twit

# Get the recent status of a user.
def get_recent_tweet(twit, username):
    user = twit.get_user(username)
    return user.status

# Announces a status to the IRC channel.
def notify_new_tweet(irc, username, tweet):
    url = "https://www.twitter.com/%s/status/%s" % (username, tweet.id)
    notification = ("@%s has posted a new tweet! \"%s...\" %s"
                    % (username, tweet.text[0:60], url_shorten(url)))
    irc.msg(notification)

# Tweets the current setlist. Called during !setprevious
# Creates a secondary, temporary tweepy API object so it can be called from
# anywhere.
def tweet_setlist():
    tmp = authorize_new_twit('text/twitter')
    
    # 140 character limit with 5 character (X/Y) taken into account
    setlist = filehandle.get_list('text/setlist')
    gig = filehandle.get_list('text/gig')[0]

    tweets = []

    msg = '%s: %s' % (gig, setlist.pop(0))

    while len(setlist) > 0:
        # Message length, (X/Y), and space in between
        if (len(msg) + len(setlist[0]) + 2) > 135:
            tweets.append(msg)
            msg = ''
            
        if msg == '':
            msg = setlist.pop(0)
        else:
            msg = '%s, %s' % (msg, setlist.pop(0))

    tweets.append(msg)

    for i, status in enumerate(tweets):
        tmp.update_status('%s (%d/%d)' % (status, i + 1, len(tweets)))
