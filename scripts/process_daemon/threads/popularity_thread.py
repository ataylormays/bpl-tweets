import csv
import os
import sys
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
	def __init__(self, club):
		super(PopularityThread, self).__init__()
		self.club = club

	def run(self):
		# at start of match
		twitter_access.build_params()
		since_id = twitter_access.update_since_id(self.club)
		# after 1st run of match, every n minutes
		runs = 1
		while(runs < constants.NUM_COLS):
			twitter_access.populate_popularity(
				club_nm=self.club,
				since_id=since_id,
				iteration=runs)
			template = "PopularityThread sleeping for %d."
			print template % (constants.RUN_FREQ * 60)
			time.sleep(constants.RUN_FREQ * 60)
			runs += 1
