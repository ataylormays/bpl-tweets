import datetime
import requests
import operator
import os, sys
import time
import logging
from bs4 import BeautifulSoup

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))

resources_path = os.path.abspath(os.path.join(BASE_DIR, 'resources'))
sys.path.append(resources_path)
import constants

import_dirs = [constants.UTILITIES_DIR, constants.THREADS_DIR]
for direc in import_dirs:
	sys.path.append(direc)

import mongo_utilities as mongodb
import post_match_processing as pmp

# initiate logging
logging.basicConfig(filename=constants.LOG_FILE, 
						level=constants.LOG_LEVEL,
						format=constants.LOG_FORMAT)

FILE_NM = "get_scores_job"

########################################################################
########## Job runs nightly to fetch scores from games #################
########################################################################

def _get_matches_without_score(collection):
	query = {"score" : { "$exists" : False }}
	matches = mongodb.query_collection(collection, query)
	return matches

def main(env="prod"):
	collection = mongodb.init_collection('archive', env)
	matches = _get_matches_without_score(collection)
	for m in matches:
		score = pmp.scrape_score(m)
		if score:
			update = {"score" : score}
			query = {"_id" : m["_id"]}
			mongodb.update_one(collection, query, update)

if __name__ == '__main__':
	main()