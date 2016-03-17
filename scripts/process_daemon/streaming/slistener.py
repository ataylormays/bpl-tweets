import json
import os, sys
import time

from tweepy import StreamListener
from tweepy import API

file_loc = os.path.abspath(__file__)
resources_path = os.path.abspath(os.path.join(
	os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))), 'resources'))
sys.path.append(resources_path)

import constants

utilities_path = os.path.abspath(os.path.join(
	constants.BASE_DIR, 'scripts/utilities'))
sys.path.append(utilities_path)

import mongo_utilities as mongo

class SListener(StreamListener):

	def __init__(
		self,
		team1,
		team2,
		match_ts, 
		users = [],
		api = None,
		fprefix = 'streamer',
		write_limit = 10,
		total_limit = 60,
		directory = os.path.dirname(
			os.path.dirname(
				os.path.dirname(
					os.path.dirname(__file__))))):
		self.api = api or API()
		self.time = time.time()
		self.start_time = time.time()
		self.write_limit = write_limit
		self.total_limit = total_limit
		self.team1 = team1
		self.team2 = team2
		self.match_ts = match_ts
		self.users = users
		self.t1_counter = 0
		self.t2_counter = 0
		team1_fix, team2_fix = map(
			lambda x: x.lower().replace(" ", "_"),
			[team1, team2])

		# db configs
		self.collection = mongo.init_collection('live')

	def on_data(self, data):
		if 'in_reply_to_status' in data:
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
				warning = json.loads(data)['warning']
				print "Warning: %s." % warning['message']
				return false


	def contains_either_team(self, text):
		t = text.lower()
		return self.team1.lower() in t or self.team2.lower() in t

	def build_document(self, status, team):
		# get dict subfield of tweepy's Status object
		tweet = json.loads(status)

		# add tweet's unix ts, the match date, and team to tweet object
		tweet["unix_ts"] = mongo.twitter_time_to_unix(tweet["created_at"])
		tweet["team"] = team
		tweet["match_ts"] = self.match_ts
		
		return tweet

	def on_status(self, status):
		totalTime = time.time() - self.start_time
		delta = time.time() - self.time

		if totalTime > self.total_limit:
			print "Time limit exceed. Terminating slistener."
			self.write_line(totalTime)
			self.data_output.close()
			self.id_output.close()
			self.tweet_output.close()
			self.user_output.close()
			self.delout.close()
			return False

		tweet = json.loads(status)
		tweet_user = tweet["user"]["id_str"]
		tweet_text = tweet['text']
		tweet_id = tweet["id_str"]

		# TO-DO: write tweet object to db
		#json.dump(status, self.tweet_json_output)

		if delta > self.write_limit:
			self.t1_counter = 0
			self.t2_counter = 0
			self.time = time.time()

		if self.team1.lower() in tweet_text.lower():
			document = self.build_document(status, self.team1)
			mongo.insert_object(self.collection, document)
			self.t1_counter += 1
		if self.team2.lower() in tweet_text.lower():
			document = self.build_document(status, self.team2)
			mongo.insert_object(self.collection, document)
			self.t2_counter += 1
		return True

	def on_delete(self, status_id, user_id):
		return

	def on_limit(self, track):
		sys.stderr.write(track + "\n")
		raise SystemError('Reached limit of API requests!')

	def on_error(self, status_code):
		sys.stderr.write("Error: " + str(status_code) + "\n")
		return False

	def on_timeout(self):
		sys.stderr.write("Timeout, sleeping for 60 seconds.\n")
		time.sleep(60)
		return
