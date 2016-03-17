import os
import sys
import threading

from random import randint

resources_path = os.path.abspath(os.path.join('../../../..', 'resources'))
streaming_path = os.path.abspath(os.path.join('..', 'streaming'))

import_paths = [resources_path, streaming_path]
for ip in import_paths:
	sys.path.append(ip)

from streaming_tweets import StreamingTweets

class LiveTweetsThread(threading.Thread):
	"""docstring for LiveTweetsThread"""
	def __init__(self, home, away, match_ts, runtime):
		threading.Thread.__init__(self)
		self.home = home
		self.away = away
		self.match_ts = match_ts
		self.runtime = runtime
		self.name = home + "_vs_" + away + "_LiveTweetThread"

	def run(self):
		streamer = StreamingTweets()
		
		#TO-DO: get list of VIP users from config file
		users = ["OptaJoe"]
		streamer.start(self.home, self.away, self.match_ts, users, self.runtime)
