#!/usr/bin/python

import csv
import datetime
import os
import sys
import time
import tweepy

resources_path = os.path.abspath(os.path.join('../..', 'resources'))
streaming_path = os.path.abspath('streaming')
twitter_access_path = os.path.abspath('threads/twitter_access')

import_paths = [resources_path, streaming_path, twitter_access_path]
for ip in import_paths:
	sys.path.append(ip)

import constants
from threads.live_tweets_thread import LiveTweetsThread as LTT
from threads.popularity_thread import PopularityThread as PT

def remove_zeropading(time_obj):
	return time_obj[1:] if time_obj[0] == '0' else time_obj

def start_threads(lt_threads, p_threads):
	template = "Starting live tweet collection for %s and %s."
	for thread in lt_threads:
		print template % (thread.home, thread.away)
		thread.start()
	template = "Starting popularity measuring for %s."
	for thread in popularitythreads:
		print template % thread.club
		thread.start()

def read_matches(filename, now, today):
	with open(filename, "r") as f:
		matches_reader = csv.reader(f, delimiter=",")
		curr_matches = []
		for row in matches_reader:
			if row[0] != today:
				continue
			if row[1] != now:
					continue
			curr_matches += [[row[2], row[3]]]

loop = True

while True:
	today = datetime.date.today().strftime("%d %B %Y")
	now = datetime.datetime.now().strftime("%I:%M %p")

	now = remove_zeropading(now)
	today = remove_zeropading(today)

	try:
		filename = os.path.join(constants.MATCHES_DIR, "matches.csv")
		matches = read_matches(filename, now, today)

		if matches:
			lt_threads = [
				LTT(
					m[0],
					m[1],
					constants.SECRETS_DIR,
					seconds)
				for m in matches]

			p_threads = [PT(m[0]) for m in matches]
			p_threads += [PT(m[1]) for m in matches]

			start_threads(lt_threads, p_threads)

	except:
		print "Daemon caught exception. Ending process."
		raise
		loop = False

	if loop:
		print "Daemon sleeping for 30 seconds."
		time.sleep(30)
	else:
		break
