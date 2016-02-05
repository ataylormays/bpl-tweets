import csv
import os, sys
from collections import Counter

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))

resources_path = os.path.abspath(os.path.join(BASE_DIR, 'resources'))
sys.path.append(resources_path)
import constants

db_path = os.path.join(BASE_DIR, 'scripts/utilities')
sys.path.append(db_path)
import mongo_utilities as mongodb

def init_collection():
	if constants.LIVE_MODE:
		db_name = constants.TWITTER_DB
		collection_name = constants.TWITTER_COLLECTION
	else:
		db_name = constants.TWITTER_TEST_DB
		collection_name = constants.TWITTER_TEST_COLLECTION#LIVE_TEST_COLLECTION
	db = mongodb.get_db(db_name)
	collection = mongodb.get_collection(db, collection_name)
	
	return collection

def get_matches():
	matches_filename = os.path.join(constants.MATCHES_DIR, "matches.csv")
	matches = []
	with open(matches_filename, "r") as f:
		matches_reader = csv.reader(f, delimiter=",")
		for row in matches_reader:
			match = {"date" : row[0], 
				"home" : row[2], 
				"away" : row[3]
			}
			matches += [match]

	return matches

def get_tweets_for_match(match):
	collection = init_collection()
	query = {"match_date" : match["date"], 
		"$or": [{"team" : match["home"]},
				{"team" : match["away"]}
				]}
	result = mongodb.query_collection(collection, query)
	return result

'''
find_top_hashtags: function to return most popular hashtags from
	a set of tweets
	
input: 
	num_hashtags (int), number of hashtags desired in result
	tweets (list of dicts), tweet objects
output:
	sorted list of dicts for easy output to json
	each dict is has the rank, text, and number of occurences of the hashtag
'''
def find_top_hashtags(num_hashtags, tweets):
	all_hashtags = []
	for tweet in tweets:
		for hashtag in tweet["entities"]["hashtags"]:
			all_hashtags += [hashtag["text"]]

	hashtags_counter = Counter(all_hashtags)
	sorted_top_hashtags = hashtags_counter.most_common(num_hashtags)

	top_hashtags = []
	for index, hashtag in enumerate(sorted_top_hashtags):
		hashtag_dict = {"rank": index+1,
						"text": hashtag[0],
						"count": hashtag[1]}
		top_hashtags += [hashtag_dict]


def process_tweets_for_match(tweets):
