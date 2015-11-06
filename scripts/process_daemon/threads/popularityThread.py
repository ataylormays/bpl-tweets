import threading
import csv
import time
import os, sys

resources_path = os.path.abspath(os.path.join('../..', 'resources'))
sys.path.append(resources_path)

import constants, twitteraccess

class PopularityThread(threading.Thread):
	"""docstring for PopularityThread"""
	def __init__(self, club):
		super(PopularityThread, self).__init__()
		self.club = club

	def run(self):
		# at start of match
		twitteraccess.build_params()
		twitteraccess.update_since_id(self.club)
		
		# after 1st run of match, every n minutes
		since_id = twitteraccess.get_since_id(self.club)
		
		runs = 1
		while(runs < constants.NUM_COLS):
			twitteraccess.populate_popularity(club_nm=self.club, since_id=since_id, iteration=runs)
			time.sleep(constants.RUN_FREQ * 60)
			runs += 1
			