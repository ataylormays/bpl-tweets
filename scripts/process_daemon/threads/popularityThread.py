import threading
import csv
import time
import os, sys

resources_path = os.path.abspath(os.path.join('../../..', 'resources'))
twitteraccess_path = os.path.abspath('twitteraccess')
for p in [resources_path, twitteraccess_path]:
	sys.path.append(p)

import constants
import twitteraccess

class PopularityThread(threading.Thread):
	"""docstring for PopularityThread"""
	def __init__(self, club):
		super(PopularityThread, self).__init__()
		self.club = club

	def run(self):
		# at start of match
		twitteraccess.build_params()
		since_id = twitteraccess.update_since_id(self.club)
		
		# after 1st run of match, every n minutes
		runs = 1
		while(runs < constants.NUM_COLS):
			twitteraccess.populate_popularity(club_nm=self.club, since_id=since_id, iteration=runs)
			print "PopularityThread sleeping for %d" % (constants.RUN_FREQ * 60)
			time.sleep(constants.RUN_FREQ * 60)
			runs += 1