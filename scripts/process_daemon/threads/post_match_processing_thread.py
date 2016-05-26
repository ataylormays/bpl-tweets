import os, sys
import time
import threading
import logging

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file_loc))))

resources_path = os.path.abspath(os.path.join(BASE_DIR, 'resources'))
sys.path.append(resources_path)
import constants

sys.path.append(constants.UTILITIES_DIR)
import post_match_processing as pmp
import mongo_utilities as mongo

# initiate logging
logging.basicConfig(filename=constants.LOG_FILE, 
						level=constants.LOG_LEVEL,
						format=constants.LOG_FORMAT)

FILE_NM = "post_match_processing_thread"

class PostMatchProcessingThread(threading.Thread):
	"""docstring for PostMatchProcessingThread"""
	def __init__(self, match):
		threading.Thread.__init__(self)
		self.match = match

	def run(self):
		log_prefix = FILE_NM + ":run: "
		#time.sleep(constants.TOT_MINUTES * 60)
		matches_collection = mongo.init_collection('matches')
		update = {"live" : False}
		query = {"home" : self.match["home"],
					"away" : self.match["away"],
					"timestamp" : self.match["timestamp"]}
		logging.debug(log_prefix + "query: " + str(query))
		updated_record = mongo.update_one(matches_collection, query, update)
		processed_record = pmp.process_match(self.match)
		logging.debug(log_prefix + "processed_record: " + str(processed_record))
		archive_collection = mongo.init_collection('archive')
		mongo.insert_object(archive_collection, processed_record)

if __name__ == '__main__':
	matches_collection = mongo.init_collection('matches')
	matches = mongo.query_collection(matches_collection)[-11:-1]
	for m in matches:
		print m
		t = PostMatchProcessingThread(m)
		t.run()
