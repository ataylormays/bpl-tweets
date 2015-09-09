from slistener import SListener
import time, tweepy, sys

## authentication
consumer_key = '2IrJvoGvLc1YNDq2huog7KH7j'
consumer_secret = 'z3eKAKrhEx9xnw0eNsfwzxx31P281bHomUNKEC6qZevcofuEaW'
access_token = '3105547012-EkZOfGoF7XpqqFt6Hd00ULS6fBJOEYdFPQ2jAHp'
access_token_secret = 'l0RaCGbYqpPhCxeN6KgiQx1WpwCCMr1b4YOJGzZPQ42Dp'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def start(teams = [], users = []):
 
    listen = SListener(api=api, team1=teams[0], team2=teams[1], users = users)
    stream = tweepy.Stream(auth, listen)

    print "Streaming started..."

    try: 
        if teams and users:
            print 'got both'
            stream.filter(track = teams, follow = users)
        elif users:
            stream.filter(follow = users)
        elif teams:
            stream.filter(track = teams)
    except:
        e = sys.exc_info()[0]
        print "error!"
        print e
        stream.disconnect()

if __name__ == '__main__':
    home = "manchester united"
    away = "tottenham hotspur"
    users = ["OptaJoe"]
    users_ids = [user.id_str for user in [api.get_user(screen_name) for screen_name in users]]
    teams = [home, away]
    start(teams = teams, users = users_ids)

