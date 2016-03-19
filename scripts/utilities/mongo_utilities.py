from pymongo import MongoClient, ReturnDocument
import pymongo
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
	unix_ts = time.mktime(t)
	return unix_ts

if __name__ == '__main__':
	collection = init_collection('matches')
	matches = query_collection(collection)
	mtime = 1457190000 - 13
	start = mtime - 30
	end = mtime + 30
	query = {"timestamp": {"$lt": end, "$gt": start}, "home":"Chelsea"}
	ms = query_collection(collection, query={"timestamp":{"$gt": time.time()}})
	update = {"live" : False}
	#updated_record = update_one(collection, query, update)
	for m in ms:
		print m
		
	# for m in matches:
	# 	print m