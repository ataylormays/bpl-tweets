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

# initiate logging
logging.basicConfig(filename=constants.LOG_FILE, 
						level=constants.LOG_LEVEL,
						format=constants.LOG_FORMAT)

FILE_NM = "popularity_thread"

class PopularityThread(threading.Thread):
	"""docstring for PopularityThread"""
	def __init__(self, club, match_ts):
		super(PopularityThread, self).__init__()
		self.club = club
		self.name = club + "_PopularityThread"
		self.match_ts = match_ts

	def run(self):
		log_prefix = FILE_NM + ":run: "

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
			template = " sleeping for %d."
			log.debug(log_prefix + self.name + template % (constants.RUN_FREQ * 60))
			time.sleep(constants.RUN_FREQ * 60)
			runs += 1
