import json
import os
import sys
import time
import tweepy

from slistener import SListener

resources_path = os.path.abspath(os.path.join('../../..', 'resources'))
sys.path.append(resources_path)

import constants

class StreamingTweets:
	"""docstring for StreamingTweets"""
	def __init__(
		self,
		consumer_key,
		consumer_secret,
		access_token,
		access_token_secret):

		self.consumer_key = consumer_key
		self.consumer_secret = consumer_secret
		self.access_token = access_token
		self.access_token_secret = access_token_secret

	def start(self, home, away, users = [], runtime=30):
		auth = tweepy.OAuthHandler(
			self.consumer_key, self.consumer_secret)
		auth.set_access_token(
			self.access_token, self.access_token_secret)

		api = tweepy.API(auth)
		users_ids = [
			user.id_str
			for user in [
				api.get_user(screen_name)
				for screen_name in users]]

		listen = SListener(
			api=api,
			team1=home,
			team2=away,
			users = users_ids,
			total_limit=runtime)
		stream = tweepy.Stream(auth, listen)

		print "Streaming started for %s vs %s." % (home, away)

		teams = [home, away]
		try:
			if teams and users:
				stream.filter(
					track = teams,
					follow = users_ids,
					languages=['en'])
			elif users:
				stream.filter(
					follow = users_ids,
					languages=['en'])
			elif teams:
				stream.filter(
					track = teams,
					languages=['en'])
		except:
			print "StreamingTweets caugh exception. Ending process."
			stream.disconnect()
			raise
