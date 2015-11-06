from tweepy import StreamListener
from tweepy import API
import json, time, sys, os, json

class SListener(StreamListener):


    def __init__(self, team1, team2, users = [], api = None, fprefix = 'streamer', write_limit = 8, total_limit = 30,
            directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))):
        self.api = api or API()
        self.time = time.time()
        self.start_time = time.time()
        self.write_limit = write_limit
        self.total_limit = total_limit
        self.team1 = team1
        self.team2 = team2
        self.users = users
        self.t1_counter = 0
        self.t2_counter = 0
        self.fprefix = directory + '/data/streaming_data/' + fprefix + '_' +  team1.lower().replace(' ', '_') + '_' + team2.lower().replace(' ', '_')
        self.data_output  = open(self.fprefix + '_' 
                            + time.strftime('%Y-%m-%d_%H-%M-%S') + '.txt', 'w')
        self.id_output  = open(self.fprefix + '_ids.txt', 'w')
        self.tweet_output  = open(self.fprefix + '_tweets.txt', 'w')
        self.user_output = open(self.fprefix + '_users.txt', 'w')
        
        self.delout  = open(self.fprefix + '_delete.txt', 'w')

    def on_data(self, data):
        print 'found data'

        if  'in_reply_to_status' in data:
            print 'heading to on_status'
            if self.on_status(data) is False:
                return False
        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
        elif 'warning' in data:
            warning = json.loads(data)['warnings']
            print warning['message']
            return false

    def on_status(self, status):
        if time.time() - self.start_time > self.total_limit:
            print "over time limit"
            self.data_output.close()
            self.user_output.close()
            self.id_output.close()
            return False

        tweet = json.loads(status)

        # if tweet is from VIP user about team 1 or team 2
        if ( tweet["user"]["id_str"] in self.users 
            and ( self.team1.lower() in tweet['text'].lower() 
                or self.team2.lower() in tweet['text'].lower() )):
                #write tweet id to user file
                self.user_output.write(tweet["id_str"] + ', ')
        
        print tweet["id_str"]

        self.id_output.write(tweet["id_str"] + ', ')
        self.tweet_output.write(tweet["text"].encode('utf-8') + ', ')

        if time.time() - self.time > self.write_limit:
            print "inside first if"
            print "time diff is ", str(time.time() - self.time)
            self.data_output.write(str(time.time() - self.start_time) +', ' + str(self.t1_counter) + ', ' + str(self.t2_counter) + ',\n')
            self.t1_counter = 0
            self.t2_counter = 0
            self.time = time.time()

        if self.team1.lower() in tweet['text'].lower():
            self.t1_counter += 1
            print "incrementing t1_counter"
        if self.team2.lower() in tweet['text'].lower():
            print "incrementing t2_counter"
            self.t2_counter += 1

        print "exiting on_status successfully"
        return True            

    def on_delete(self, status_id, user_id):
        print "in on_delete"
        self.delout.write( str(status_id) + "\n")
        return

    def on_limit(self, track):
        print "in on_limit"
        sys.stderr.write(track + "\n")
        return

    def on_error(self, status_code):
        print "in on_error"
        sys.stderr.write('Error: ' + str(status_code) + "\n")
        return False

    def on_timeout(self):
        print "in on_timeout"
        sys.stderr.write("Timeout, sleeping for 60 seconds...\n")
        time.sleep(60)
        return