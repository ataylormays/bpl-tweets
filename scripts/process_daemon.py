import datetime
import csv
import os, sys
import time
import tweepy

path_resources = os.path.abspath(os.path.join('..', 'resources'))
path_streaming = os.path.abspath(os.path.join('..', 'epl_twitter/streaming'))
import_paths = [path_resources, path_streaming]
for ip in import_paths:
	sys.path.append(ip)

try:
	import constants, streaming
except ImportError, e:
	print 'sys_path: ', sys.path
	constants = __import__('constants')
	print 'constants: %r' % constants
	try:
		print 'constants is at %s (%s)' % (constants.__file__, constants.__path__)
	except Exception, e:
		print 'Cannot give details on constants (%s)' % e

def remove_zeropading(time_obj):
	return time_obj[1:] if time_obj[0] == '0' else time_obj

loop = True

consumer_key = '2IrJvoGvLc1YNDq2huog7KH7j'
consumer_secret = 'z3eKAKrhEx9xnw0eNsfwzxx31P281bHomUNKEC6qZevcofuEaW'
access_token = '3105547012-EkZOfGoF7XpqqFt6Hd00ULS6fBJOEYdFPQ2jAHp'
access_token_secret = 'l0RaCGbYqpPhCxeN6KgiQx1WpwCCMr1b4YOJGzZPQ42Dp'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
home = "manchester united"
away = "tottenham hotspur"
users = ["OptaJoe"]
users_ids = [user.id_str for user in [api.get_user(screen_name) for screen_name in users]]
runtime = 60*int(constants.TOT_MINUTES)

while(loop):
	today = datetime.date.today().strftime("%d %B %Y") 
	now = datetime.datetime.now().strftime("%I:%M %p")

	now = remove_zeropading(now)
	today = remove_zeropading(today)

	try:
		f = open(os.path.join(constants.MATCHES_DIR, "matches.csv"), 'r')
		matches_reader = csv.reader(f, delimiter=",")
		for row in matches_reader:
			if row[0] != today:
				continue
			if row[1] != now:
				continue
			home, away = row[2], row[3]
			# start processes with home and away
			print "start processes with %s and %s" % (home, away)
			teams = [home, away]

			streaming.start(teams = teams, users = users_ids, runtime=runtime)

		f.close()

	except:
		print "Ending process"
		loop = False
	print "Sleeping for 30 secs"
	time.sleep(30)



