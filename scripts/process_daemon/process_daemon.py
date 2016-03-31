#!/usr/bin/python

import argparse
import csv
import time
import os
import sys
import time
import tweepy

file_loc = os.path.abspath(__file__)
parent_directory = os.path.dirname(file_loc)
streaming_path = os.path.join(parent_directory, 'streaming')
resources_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(parent_directory)), 'resources'))
twitter_access_path = os.path.join(parent_directory, 'threads/twitter_access')

import_paths = [resources_path, streaming_path, twitter_access_path]
for ip in import_paths:
	sys.path.append(ip)

import constants
sys.path.append(constants.UTILITIES_DIR)
import mongo_utilities as mongo

from threads.live_tweets_thread import LiveTweetsThread as LTT
from threads.popularity_thread import PopularityThread as PT
from threads.post_match_processing_thread import PostMatchProcessingThread as PMPT

def set_live_in_db(collection, matches, live):
	update = {"live": live}
	for m in matches:
		query = {"home" : m["home"],
					"away" : m["away"],
					"timestamp" : m["timestamp"]}
		updated_record = mongo.update_one(collection, query, update)

def start_threads(lt_threads, p_threads, pmp_threads):
	live_template = "Starting live tweet collection for %s and %s."
	for thread in lt_threads:
		print live_template % (thread.home, thread.away)
		thread.start()
	popularity_template = "Starting popularity measuring for %s."
	for thread in p_threads:
		print popularity_template % thread.club
		thread.start()
	post_match_template = "Starting post-match for %s vs %s"
	for thread in pmp_threads:
		print post_match_template % (thread.match["home"], thread.match["away"])
		thread.start()

def dummy_mode():
	# TODO - Implement!
	pass

def team_mode(team1, team2, match_ts):
	lt_thread = LTT(
		team1,
		team2,
		match_ts,
		60 * constants.TOT_MINUTES)
	p_threads = [PT(team1, match_ts), PT(team2, match_ts)]

	start_threads([lt_thread], p_threads, None)

def daemon_mode():
	loop = True

	live_threads = []
	while True:
		now = int(time.time())
		start = now - 30;
		end = now + 30;
		collection = mongo.init_collection('matches')
		query = {"timestamp": {"$lt": end, "$gt": start}}
		matches = mongo.query_collection(collection, query)
		try:
			if matches:
				lt_threads = [
					LTT(
						m["home"],
						m["away"],
						m["timestamp"],
						60 * constants.TOT_MINUTES)
				for m in matches]

				p_threads = [PT(m["home"], m["timestamp"]) for m in matches]
				p_threads += [PT(m["away"], m["timestamp"]) for m in matches]

				pmp_threads = [PMPT(m) for m in matches]

				set_live_in_db(collection, matches, live=True)
				start_threads(lt_threads, p_threads, pmp_threads)
				for t in live_threads:
					t.processed = t.isAlive()
				live_threads = [t for t in p_threads if not t.processed]

		except:
			print "Daemon caught exception. Ending process."
			set_live_in_db(collection, matches, live=False)
			raise
			loop = False

		if loop:
			print "Daemon sleeping for 55 seconds."
			time.sleep(55)
		else:
			break

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-t1",
		"--team1",
		type=str,
		help="Team 1 to collect tweets from, if ignoring matches file.")
	parser.add_argument(
		"-t2",
		"--team2",
		type=str,
		help="Team 2 to collect tweets from, if ignoring matches file.")
	parser.add_argument(
		"-mts",
		"--match_timestamp",
		type=str,
		help="Timestamp of match if in teammode.")
	parser.add_argument(
		"-d",
		"--dummy",
		action="store_true",
		help="Run the process_daemon in dummy mode.")
	args = parser.parse_args()

	dummy = args.dummy
	team1 = args.team1
	team2 = args.team2
	match_timestamp = args.match_timestamp

	error1 = "Do not specify --team1 or --team2 in dummy mode."
	error2 = "--team1 and --team2 must be specified together or not at all."
	if dummy:
		if team1 or team2:
			print error1, "Exiting."
			sys.exit(1)
	elif (team1 and not team2) or (team2 and not team1):
		print error2, "Exiting."
		sys.exit(1)

	if dummy:
		dummy_mode()
	elif team1:
		team_mode(team1, team2, match_ts=match_timestamp)
	else:
		daemon_mode()

if __name__ == "__main__":
	main()
	#t = LTT("Manchester United", "Arsenal", int(time.time()), 15)
	#t = PT("Manchester United")
	#t.start()
