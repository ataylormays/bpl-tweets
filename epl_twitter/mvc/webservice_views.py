from django.http import JsonResponse, Http404
import json
import time
import operator
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

def start_and_end(request):
	try:
		start = int(request.GET.get('start'))
		end = int(request.GET.get('end'))

		collection = mongodb.init_collection("twitter")
		query = {"unix_ts": {"$lt": end, "$gt": start}}
		result = mongodb.query_collection(collection, query)
		
		# serialize result
		for r in result:
			r["_id"] = str(r["_id"])
		
		return JsonResponse(result, safe=False)
	except:
		raise Http404("Internal Server Error")

def find_match(team1, team2=None, match_ts=None):	
	matches_collection = mongodb.init_collection('matches')

	team1 = team1.replace("_", " ").title()
	if team2:
		team2 = team2.replace("_", " ").title()

        query = { "$or" :
                   [ { "timestamp" : match_ts,
                       "home" : team1 },
                     { "timestamp" : match_ts,
                       "away" : team2 } ] }

	result = mongodb.query_collection(matches_collection, query)        
	return result[0]

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
		collection = mongodb.init_collection("live")

		home = request.GET.get('home').replace("_", " ").title()
		away = request.GET.get('away').replace("_", " ").title()

		match_ts = int(request.GET.get('match_ts'))
		default_start = match_ts

		if 'start' in request.GET:
			query_start = int(request.GET.get('start'))
		else:
			query_start = default_start

                now = time.time()
		end = min(now, default_start + 120 * 60)

		if now < query_start:
			return JsonResponse(None, safe=False)

		home_counts, away_counts = [], []
		ts_chunks = chunks(query_start, end, 60)
		for i in xrange(len(ts_chunks)-1):
			start = ts_chunks[i]
			end = ts_chunks[i+1]
			home_query = {"unix_ts": {"$lt": end, "$gt": start}, 
							"team" : home}
			away_query = {"unix_ts": {"$lt": end, "$gt": start}, 
							"team" : away}
			home_tweets = mongodb.query_collection(collection, home_query)
			away_tweets = mongodb.query_collection(collection, away_query)
			home_counts += [len(home_tweets)]
			away_counts += [len(away_tweets)]
		result = {
		    "home" : {"club":home, "counts":home_counts},
		    "away" : {"club":away, "counts":away_counts},
		    "start" : query_start,
		    "end" : end}

		return JsonResponse(result, safe=False)

	except:
		raise Http404("Internal Server Error")

def find_most_popular_tweet(tweets, start_index=None, end_index=None):
	popularity_dict = {}
	for t in tweets:
		# iterate backwards down popularity_progression to get
		# last popularity for tweet
		start = start_index if start_index else 0
		end = end_index if end_index else constants.TOT_MINUTES
		popularity_progression = t["popularity_progression"][start:end][::-1]
		for index, popularity in enumerate(popularity_progression):
			if index != 0:
				popularity_dict[t["id_str"]] = popularity
	sorted_tweets = sorted(popularity_dict, key=popularity_dict.get)
	sorted_tweets.reverse()
	return sorted_tweets[0]

def most_popular_tweet(request):
	try:
		body = json.loads(request.body)
		
		# required params
		club = body["club"]
		match_ts = body["match_timestamp"]

		# optional params
		since_ts = body["since_ts"] if "since_ts" in body else None
		exclusions = body["exclusions"] if "exclusions" in body else []

		collection = mongodb.init_collection("popular")
		query = {"club" : club,
                         "match_ts" : match_ts,
                         "id_str" : {"$nin" : exclusions}
                }
		tweets = mongodb.query_collection(collection, query)

		if len(tweets) == 0:
			return JsonResponse(None, safe=False)

		# if current time is past match end, return most popular tweet
		match_end = float(match_ts) + constants.TOT_MINUTES * 60
		now = time.time()
		if match_end < now:
			top_tweet = find_most_popular_tweet(tweets)
		else:
			# if since_ts was provided, return most popular tweet over that time period
			# else, return most popular tweet of the match
			if since_ts:
				time_window = time.time() - float(since_ts)
				num_minutes = int(time_window / 60)
				start_index = int((float(since_ts) - match_ts) / 60)
				end_index = start_index + num_minutes
				top_tweet = find_most_popular_tweet(tweets, start_index, end_index)
			else:
				top_tweet = find_most_popular_tweet(tweets)

		result = {"club" : club,
                          "num_tweets" : len(tweets),
                          "top_tweet" : top_tweet}
		
		return JsonResponse(result, safe=False)
	except:
		raise Http404("Internal Server Error")

