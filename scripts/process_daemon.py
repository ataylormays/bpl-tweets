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

import constants
from threads.liveTweetsThread import LiveTweetsThread as LTT

# t1 = LTT("manchester united", "arsenal", constants.SECRETS_DIR, 60*constants.TOT_MINUTES)
# t1.start() 

def remove_zeropading(time_obj):
	return time_obj[1:] if time_obj[0] == '0' else time_obj

loop = True

while(loop):
	today = datetime.date.today().strftime("%d %B %Y") 
	now = datetime.datetime.now().strftime("%I:%M %p")

	now = remove_zeropading(now)
	today = remove_zeropading(today)

	try:
		f = open(os.path.join(constants.MATCHES_DIR, "matches.csv"), 'r')
		matches_reader = csv.reader(f, delimiter=",")
		curr_matches = []
		for row in matches_reader:
			if row[0] != today:
				continue
			if row[1] != now:
				continue
			curr_matches += [[row[2], row[3]]]
		if curr_matches:
			livetweetthreads = [LTT(m[0], m[1], constants.SECRETS_DIR, 60*constants.TOT_MINUTES) for m in curr_matches]
			for thread in livetweetthreads:
				print "starting processes with %s and %s" % (thread.home, thread.away)
				thread.run()
		f.close()

	except:
		print "Ending process"
		loop = False
		break
	print "Sleeping for 30 secs"
	time.sleep(30)



