from pymongo import MongoClient, ReturnDocument
import pymongo
import time, calendar
import os, sys

file_loc = os.path.abspath(__file__)
resources_path = os.path.join(
	os.path.dirname(os.path.dirname(os.path.dirname(file_loc))), 'resources')
sys.path.append(resources_path)
import constants

def get_db(database_name, server_url=None):
	client = MongoClient(server_url)
	return client[database_name]

def get_collection(db, collection_name):
	return db[collection_name]

def init_collection(collection_type):
	if constants.LIVE_MODE:
		env = 'prod'
	if constants.QA_MODE:
		env = 'qa'

	db_name = constants.TWITTER_DB[env]
	collection_name = constants.TWITTER_COLLECTIONS[env][collection_type]
	db = get_db(db_name)
	collection = get_collection(db, collection_name)

	return collection

def insert_object(collection, object):
	assert (type(object) == dict or 
		type(object) == list)

	if type(object) == dict:
		collection.insert_one(object)

	elif type(object) == list:
		collection.insert_many(object)

def query_collection(collection, query=None, sort=None):
	results = collection.find(query).sort(sort) if sort else collection.find(query)
	return [doc for doc in results]

def update_one(collection, query, update):
	updated_document = collection.find_one_and_update(filter=query, \
			update={'$set':update}, \
			return_document=ReturnDocument.AFTER)
	return updated_document


def twitter_time_to_unix(created_at):
	t = time.strptime(created_at, constants.TWITTER_TIME_FORMAT)
	unix_ts = calendar.timegm(t)
	return unix_ts

if __name__ == '__main__':
	matches_collection = init_collection('matches')
	new_match = {"home":"Manchester United",
					"away":"Manchester City",
					"date":"30 March 2016",
					"timestamp": int(time.time())}
	live_query = {"match_ts":1459396398}
	# live_query = {"team" : "Manchester United"}
	# live_query = {'unix_ts': {'$gt': 1459397958.0, '$lt': 1459398018.0}, 'team': u'manchester_city'}
	live_collection = init_collection('live')
	match_query = {'$or': [{'home': u'Manchester City'}, {'away': u'Manchester City'}]}
	matches = query_collection(matches_collection, match_query)
	tweets = query_collection(live_collection, live_query)
	# for m in matches:
	# 	print m
	print tweets[81]["team"]
