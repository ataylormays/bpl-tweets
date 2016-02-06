from django.http import JsonResponse, Http404
import json
import time
import csv
import os, sys

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))
resources_path = os.path.join(BASE_DIR, 'resources')
sys.path.append(resources_path)
db_path = os.path.join(BASE_DIR, 'scripts/utilities')
sys.path.append(db_path)
import mongo_utilities as mongodb
import constants

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

def find_match(team1, team2):	
	matches_filename = os.path.join(constants.MATCHES_DIR, "matches.csv")

	team1 = team1.replace("_", " ").title()
	team2 = team2.replace("_", " ").title()
	
	with open(matches_filename, "r") as f:
		matches_reader = csv.reader(f, delimiter=",")
		for row in matches_reader:
			match = {
                                "date" : row[0],
				"time" : row[1], 
				"timestamp" : row[2],
				"home" : row[3], 
				"away" : row[4]
			}
			if ((match["home"] == team1 and match["away"] == team2)
                            or match["home"] == team2 and match["away"] == team1):
				return match
			
	return None

def get_match_ts(match):
	match_dt = match["date"] + " " + match["time"]
	
	# sample dt: 17 January 2016 10:15 AM
	match_dt_format = "%d %B %Y %I:%M %p"
	t = time.strptime(match_dt, match_dt_format)
	match_ts = time.mktime(t) + 6 * 60*60

	return match_ts

def chunks(start, end, chunk_size):
	chunks = []
	while(start < end):
		chunks += [start]
		start += chunk_size
	chunks += [end]
	
	return chunks


def live_tweets_count(request):
	try:
		collection = init_collection()

		home = request.GET.get('home')
		away = request.GET.get('away')

                match = find_match(home, away)
                match_ts = match["timestamp"]
                default_start = float(match_ts)

		if 'start' in request.GET:
			query_start = int(request.GET.get('start'))
		else:
			query_start = default_start

		now = time.time()
		end = min(now, default_start + 120 * 60)

		if now < query_start:
                        return JsonResponse(None, safe=False)
			#raise Http404("Invalid request. Start parameter must be less than current time, %s" % now)

		counts = []
		ts_chunks = chunks(query_start, end, 60)
		for i in xrange(len(ts_chunks)-1):
			start = ts_chunks[i]
			end = ts_chunks[i+1]
			query = {"unix_ts": {"$lt": end, "$gt": start}, 
						"$or": [{"team" : home},
								{"team" : away}
								]}
			tweets = mongodb.query_collection(collection, query)
			counts += [len(tweets)]

                result = {
                        "home" : home,
                        "away" : away,
                        "start" : query_start,
                        "end" : end,
                        "counts" : counts}
		return JsonResponse(result, safe=False)

	except:
                raise
