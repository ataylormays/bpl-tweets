from django.http import JsonResponse, Http404
import json
import time
import os, sys

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))
resources_path = os.path.join(BASE_DIR, 'resources')
sys.path.append(resources_path)
db_path = os.path.join(BASE_DIR, 'scripts/utilities')
sys.path.append(db_path)
import test_db_connection as mongodb
import constants
print sys.path

import constants

def init_collection():
	if constants.LIVE_MODE:
		db_name = constants.TWITTER_DB
		collection_name = constants.TWITTER_COLLECTION
	else:
		db_name = constants.TWITTER_TEST_DB
		collection_name = constants.TWITTER_TEST_COLLECTION
	db = mongodb.get_db(db_name)
	collection = mongodb.get_collection(db, collection_name)
	
	return collection

def start_and_end(request):
	try:
		start = int(request.GET.get('start'))
		end = int(request.GET.get('end'))

		collection = init_collection()
		query = {"unix_ts": {"$lt": end, "$gt": start}}
		result = mongodb.query_collection(collection, query)

		# serialize result
		for r in result:
			r["_id"] = str(r["_id"])
		
		return JsonResponse(result, safe=False)
	except:
		raise Http404("Internal Server Error")

def live_tweets_count(request):
	try:
		team1 = request.GET.get('home')
		team2 = request.GET.get('away')

		now = time.time()

	except:
		raise Http404("Internal Server Error")
