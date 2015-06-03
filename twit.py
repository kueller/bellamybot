import tweepy
import filehandle
from setlistfm import url_shorten

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

def get_recent_tweet(twit, username):
    user = twit.get_user(username)
    return user.status

def notify_new_tweet(irc, username, tweet):
    url = "https://www.twitter.com/%s/status/%s" % (username, tweet.id)
    notification = ("@%s has posted a new tweet! \"%s...\" %s"
                    % (username, tweet.text[0:60], url_shorten(url)))
    irc.msg(notification)
