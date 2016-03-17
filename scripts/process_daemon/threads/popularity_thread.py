import os, sys
import threading
import time

resources_path = os.path.abspath(os.path.join('../../..', 'resources'))
twitter_access_path = os.path.abspath('twitter_access')

import_paths = [resources_path, twitter_access_path]
for ip in [resources_path, twitter_access_path]:
	sys.path.append(ip)

import constants
import twitter_access

class PopularityThread(threading.Thread):
	"""docstring for PopularityThread"""
	def __init__(self, club, match_ts):
		super(PopularityThread, self).__init__()
		self.club = club
		self.name = club + "_PopularityThread"
		self.match_ts = match_ts

	def run(self):
		# at start of match
		runs = 0
		api = twitter_access.authorize_api(runs)
		since_id = twitter_access.get_first_id(api, self.club)
		
		while(runs < constants.NUM_COLS):
			twitter_access.populate_popularity(
				club_nm=self.club,
				since_id=since_id,
				iteration=runs,
				match_ts=self.match_ts)
			template = "PopularityThread sleeping for %d."
			print template % (constants.RUN_FREQ * 60)
			time.sleep(constants.RUN_FREQ * 60)
			runs += 1
