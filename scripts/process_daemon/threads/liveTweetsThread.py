import threading
import csv
import os, sys

resources_path = os.path.abspath(os.path.join('../../../..', 'resources'))
streaming_path = os.path.abspath(os.path.join('..', 'streaming'))
import_paths = [resources_path, streaming_path]
for ip in import_paths:
	sys.path.append(ip)

from StreamingTweets import StreamingTweets

class LiveTweetsThread(threading.Thread):
	"""docstring for LiveTweetsThread"""
	def __init__(self, home, away, secrets_dir, runtime):
		threading.Thread.__init__(self)
		self.home = home
		self.away = away
		self.secrets_dir = secrets_dir
		self.runtime = runtime

	def run(self):
		with open(self.secrets_dir + 'secrets.csv', 'r+') as f:
			rows = csv.reader(f)
			secrets = [row for row in rows]
		
		secret = secrets[0]
		streamer = StreamingTweets(secret[0], secret[1], secret[2], secret[3])

		#TO-DO: get list of VIP users from config file
		users = ["OptaJoe"]
		streamer.start(self.home, self.away, users, self.runtime)
		