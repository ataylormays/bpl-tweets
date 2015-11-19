import json
import os
import sys
import time

from tweepy import StreamListener
from tweepy import API

class SListener(StreamListener):

	def __init__(
		self,
		team1,
		team2,
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
		self.users = users
		self.t1_counter = 0
		self.t2_counter = 0
		team1_fix, team2_fix = map(
			lambda x: x.lower().replace(" ", "_"),
			[team1, team2])
		self.fprefix = os.path.join(
			os.path.dirname(directory),
			"data/streaming_data/",
			"-".join([fprefix, team1_fix, team2_fix]))

		self.data_output = open(self.fprefix + '-counts_data.txt', 'w')
		self.id_output = open(self.fprefix + '-ids.txt', 'w')
		self.tweet_output = open(self.fprefix + '-tweets.txt', 'w')
		self.user_output = open(self.fprefix + '-users.txt', 'w')
		self.delout = open(self.fprefix + '-delete.txt', 'w')

	def on_data(self, data):
		if	'in_reply_to_status' in data:
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
				print "Warning: %s." % warning['message']
				return false

	def write_and_flush(self, f, s):
		f.write(s)
		f.flush()

	def write_line(self, delta):
		join = [str(delta), str(self.t1_counter), str(self.t2_counter), '\n' ]
		output = ','.join(join)
		self.write_and_flush(self.data_output, output)

	def contains_either_team(self, text):
		t = text.lower()
		return self.team1.lower() in t or self.team2.lower() in t

	def on_status(self, status):
		totalTime = time.time() - self.start_time
		delta = time.time() - self.time

		if totalTime > self.total_limit:
			print "Time limit exceed. Terminating slistener."
			self.write_line(delta)
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

		if tweet_user in self.users and self.contains_either_team(text):
			print "Received tweet #" + tweet_id + "."
			self.write_and_flush(self.user_output.write, tweet_id + ', ')

		self.write_and_flush(self.id_output, tweet_id + ', ')
		self.write_and_flush(self.tweet_output, tweet_text.encode('utf-8') + ', ')

		print delta
		if delta > self.write_limit:
			self.write_line(delta)
			self.t1_counter = 0
			self.t2_counter = 0
			self.time = time.time()

		if self.team1.lower() in tweet_text.lower():
			self.t1_counter += 1
		if self.team2.lower() in tweet_text.lower():
			self.t2_counter += 1
		return True

	def on_delete(self, status_id, user_id):
		self.write_and_flush(self.delout.write, str(status_id) + "\n")
		return

	def on_limit(self, track):
		sys.stderr.write(track + "\n")
		return

	def on_error(self, status_code):
		sys.stderr.write("Error: " + str(status_code) + "\n")
		return False

	def on_timeout(self):
		sys.stderr.write("Timeout, sleeping for 60 seconds.\n")
		time.sleep(60)
		return
