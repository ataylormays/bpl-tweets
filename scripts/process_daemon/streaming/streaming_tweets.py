import json
import os
import sys
import time
import tweepy

from random import randint
from slistener import SListener

resources_path = os.path.abspath(os.path.join('../../..', 'resources'))
sys.path.append(resources_path)

import constants

class StreamingTweets:
	"""docstring for StreamingTweets"""
	def __init__(self):
		with open(constants.SECRETS_JSON, 'r') as f:
			secrets = json.load(f)
		self.secrets = secrets
		self.stream = tweepy.Stream(None, None)
		self.start_time = time.time()

	def authorize_api(self, secrets):
		secret = secrets[randint(0,len(secrets)-1)]
		consumer_key = secret["consumer_key"]
		consumer_secret = secret["consumer_secret"]
		access_token = secret["access_token"]
		access_token_secret = secret["access_token_secret"]
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)

		return (api, auth)
		
	def get_user_ids(self, users, api):
		users_ids = [
			user.id_str
			for user in [
				api.get_user(screen_name)
				for screen_name in users]]
		return users_ids

	def get_stream(self, api, auth, home, away, match_date, users_ids, runtime):
		listen = SListener(
			api=api,
			team1=home,
			team2=away,
			match_date=match_date,
			users = users_ids,
			total_limit=runtime)
		
		return tweepy.Stream(auth, listen)

	def start_streaming(self, home, away, match_date, users, runtime):
		try:
			api, auth = self.authorize_api(self.secrets)
			users_ids = self.get_user_ids(users, api)
			self.stream = self.get_stream(api, auth, home, away, match_date, users_ids, runtime)

			print "Streaming started for %s vs %s." % (home, away)

			teams = [home, away]
			self.stream.filter(
					track = teams,
					follow = users_ids,
					languages=['en'])
		except:
			raise

	def start(self, home, away, match_date, users = [], runtime=30):
		try:
			self.start_streaming(home, away, match_date, users, runtime)
			
		#reached rate limit
		except SystemError:
			print 'reached rate limit, building new stream'
			new_runtime = (time.time() - self.start_time) / 60
			self.stream.disconnect()
			self.start_streaming(home, away, users, new_runtime)
		
		#all other exceptions
		except:
			print "StreamingTweets caught exception. Ending process."
			self.stream.disconnect()
			raise
