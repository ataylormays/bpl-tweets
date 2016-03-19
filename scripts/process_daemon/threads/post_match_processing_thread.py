import os, sys
import time
import threading

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file_loc))))

resources_path = os.path.abspath(os.path.join(BASE_DIR, 'resources'))
sys.path.append(resources_path)
import constants

sys.path.append(constants.UTILITIES_DIR)
import post_match_processing as pmp
import mongo_utilities as mongo

class PostMatchProcessingThread(threading.Thread):
	"""docstring for PostMatchProcessingThread"""
	def __init__(self, match):
		threading.Thread.__init__(self)
		self.match = match

	def run(self):
		time.sleep(constants.TOT_MINUTES * 60)
		matches_collection = mongo.init_collection('matches')
		update = {"live" : False}
		query = {"home" : self.match["home"],
					"away" : self.match["away"],
					"timestamp" : self.match["timestamp"]}
		updated_record = mongo.update_one(collection, query, update)
		processed_record = pmp.process_match(match)
		archive_collection = mongo.init_collection('archive')
		mongo.insert_object(archive_collection, processed_record)
