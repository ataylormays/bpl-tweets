#!/usr/bin/python

import argparse
import csv
import datetime
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
from threads.live_tweets_thread import LiveTweetsThread as LTT
from threads.popularity_thread import PopularityThread as PT

def remove_zeropading(time_obj):
	return time_obj[1:] if time_obj[0] == '0' else time_obj

def start_threads(lt_threads, p_threads):
	live_template = "Starting live tweet collection for %s and %s."
	for thread in lt_threads:
		print live_template % (thread.home, thread.away)
		thread.start()
	popularity_template = "Starting popularity measuring for %s."
	for thread in p_threads:
		print popularity_template % thread.club
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
			curr_matches += [[row[3], row[4], row[2]]]
	return curr_matches

def dummy_mode():
	# TODO - Implement!
	pass

def team_mode(team1, team2, match_ts):
	lt_thread = LTT(
		team1,
		team2,
		datetime.date.today().strftime("%d %B %Y"),
		60 * constants.TOT_MINUTES)
	p_threads = [PT(team1, match_ts), PT(team2, match_ts)]

	start_threads([lt_thread], p_threads)

def daemon_mode():
	loop = True

	while True:
		now = datetime.datetime.now().strftime("%I:%M %p")
		today = datetime.date.today().strftime("%d %B %Y")

		now = remove_zeropading(now)
		today = remove_zeropading(today)

		try:
			filename = os.path.join(
				constants.MATCHES_DIR,
				"matches.csv")
			matches = read_matches(filename, now, today)

			if matches:
				lt_threads = [
					LTT(
						m[0],
						m[1],
						today,
						60 * constants.TOT_MINUTES)
				for m in matches]

				p_threads = [PT(m[0], m[2]) for m in matches]
				p_threads += [PT(m[1], m[2]) for m in matches]

				start_threads(lt_threads, p_threads)

		except:
			print "Daemon caught exception. Ending process."
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
		"-d",
		"--dummy",
		action="store_true",
		help="Run the process_daemon in dummy mode.")
	args = parser.parse_args()

	dummy = args.dummy
	team1 = args.team1
	team2 = args.team2

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
		team_mode(team1, team2, match_ts=time.time())
	else:
		daemon_mode()

if __name__ == "__main__":
	main()
	#t = LTT("Manchester United", "Arsenal", datetime.date.today().strftime("%d %B %Y"), 15)
	#t = PT("Manchester United")
	#t.start()
