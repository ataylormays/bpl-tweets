from slistener import SListener
import time, tweepy, sys

class StreamingTweets:
    """docstring for StreamingTweets"""
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def start(self, home, away, users = [], runtime=30):

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        api = tweepy.API(auth)
        
        users_ids = [user.id_str for user in [api.get_user(screen_name) for screen_name in users]]

        listen = SListener(
            api=api,
            team1=home,
            team2=away,
            users = users_ids,
            total_limit=runtime)
        stream = tweepy.Stream(auth, listen)

        print "Streaming started for %s vs %s..." % (home, away)

        teams = [home, away]
        try: 
            if teams and users:
                print 'got both'
                stream.filter(track = teams, follow = users_ids, languages=['en'])
            elif users:
                stream.filter(follow = users_ids, languages=['en'])
            elif teams:
                stream.filter(track = teams, languages=['en'])
        except:
            e = sys.exc_info()[0]
            print "error!"
            print e
            stream.disconnect()

if __name__ == '__main__':
    home = "Newcastle United"
    away = "Norwich City"
    users = ["OptaJoe"]
    users_ids = [user.id_str for user in [api.get_user(screen_name) for screen_name in users]]
    teams = [home, away]
    start(teams = teams, users = users_ids, runtime=20)

