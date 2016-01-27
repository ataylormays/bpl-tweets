from pymongo import MongoClient
import time
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
	return db['collection_name']

def insert_object(collection, object):
	assert (type(object) == dict or 
		type(object) == list)

	if type(object) == dict:
		collection.insert_one(object)

	elif type(object) == list:
		collection.insert_many(object)

def query_collection(collection, query=None):
	results = collection.find(query)
	return [doc for doc in results]

def twitter_time_to_unix(created_at):
	t = time.strptime(created_at, constants.TWITTER_TIME_FORMAT)
	unix_ts = time.mktime(t)
	return unix_ts
