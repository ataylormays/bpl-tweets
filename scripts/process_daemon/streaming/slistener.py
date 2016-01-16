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
			"bpl-tweets-data/streaming_data/",
			"-".join([fprefix, team1_fix, team2_fix]))
		if not os.path.exists(self.fprefix):
			os.makedirs(self.fprefix)

		self.data_output = open(self.fprefix + '-counts_data.txt', 'w')
		self.id_output = open(self.fprefix + '-ids.txt', 'w')
		self.tweet_output = open(self.fprefix + '-tweets.txt', 'w')
		self.tweet_json_output = open(self.fprefix + '-tweets.json', 'w')
		self.user_output = open(self.fprefix + '-users.txt', 'w')
		self.delout = open(self.fprefix + '-delete.txt', 'w')

		# file_type, counts, ids, tweets, users, delete
		self.split_value = 10
		self.file_handles = { }
		self.lines_written = { }

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

	def write_and_flush(self, line, file_type):
		# This is the first time writing this kind of file type
		if file_type not in self.lines_written:
			self.lines_written[file_type] = 0
			self.file_handles[file_type] = open(
				os.path.join(
					self.fprefix,
					file_type + '-0.txt'),
				'w')

		lines_written = self.lines_written[file_type] + 1
		file_handle = self.file_handles[file_type]
		if lines_written % self.split_value == 0:
			n = lines_written / self.split_value
			file_handle.close()
			file_handle = open(
				os.path.join(
					self.fprefix,
					file_type + '-' + str(n) + '.txt'),
				'w')
			file_handle.write(line + '\n')
			file_handle.flush()

		self.lines_written[file_type] = lines_written
		self.file_handles[file_type] = file_handle

	def write_line(self, totalTime):
		join = [str(totalTime), str(self.t1_counter), str(self.t2_counter) ]
		output = ','.join(join)
		self.write_and_flush(output, 'counts')

	def contains_either_team(self, text):
		t = text.lower()
		return self.team1.lower() in t or self.team2.lower() in t

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

		if tweet_user in self.users:
			if self.contains_either_team(tweet_text):
				print "Received tweet #" + tweet_id + "."
				self.write_and_flush(self.user_output, tweet_id + ', ')
			else:
				return True

		self.write_and_flush(tweet_id, 'ids')
		self.write_and_flush(tweet_text.encode('utf-8'), 'tweets')

		# TO-DO: write tweet object to db
		#json.dump(status, self.tweet_json_output)

		if delta > self.write_limit:
			self.write_line(totalTime)
			self.t1_counter = 0
			self.t2_counter = 0
			self.time = time.time()

		if self.team1.lower() in tweet_text.lower():
			self.t1_counter += 1
		if self.team2.lower() in tweet_text.lower():
			self.t2_counter += 1
		return True

	def on_delete(self, status_id, user_id):
		self.write_and_flush(str(status_id), 'delete')
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
