import csv
import json
import oauth2
import os
import pickle
import sys
import time
import urllib
import urllib2
import tweepy
import logging
from random import randint

file_loc = os.path.abspath(__file__)
parent_directory = os.path.dirname(file_loc)
base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(parent_directory))))
resources_path = os.path.join(base_path, 'resources')
sys.path.append(resources_path)

import constants

sys.path.append(constants.UTILITIES_DIR)
import mongo_utilities as mongodb

# initiate logging
logging.basicConfig(filename=constants.LOG_FILE, 
						level=constants.LOG_LEVEL,
						format=constants.LOG_FORMAT)

FILE_NM = "twitter_access"

ct = 0

def convert_datetime(twitter_date):
	old_fmt = '%a %b %d %H:%M:%S +0000 %Y'
	new_fmt = '%Y-%m-%d %H:%M:%S'
	d = time.strptime(twitter_date, old_fmt)
	return time.strftime(new_fmt, d)

def get_hashtags(club_nm):
	hashtags = []
	with open(constants.CLUBS_FILE) as clubs_file:
		clubs = csv.reader(clubs_file, delimiter=",")
		for row in clubs:
			if(row[0]) == club_nm:
				hashtags.append(row[1].split(", "))
	return hashtags

def extract_hashtags(twitter_object):
	if len(twitter_object) == 0:
		return ""
	else:
		h_tags = twitter_object[0]["text"]
		for h in twitter_object[1:]:
			h_tags += ", " + h["text"]
		return h_tags

def get_first_id(api, club_nm):
	log_prefix = FILE_NM + ":get_first_id: "
	query = query_builder(club_nm)
	data = query_twitter_api(api, query, count=1)
	if len(data)==0:
		logging.info(log_prefix + "No data.") 
	else:
		return data[0].id_str

def get_since_id(club_nm):
	club_since_file = os.path.join(
		constants.SINCE_DIR,
		club_nm.lower().replace(" ", "_") + "_since_id.txt")
	if os.path.exists(club_since_file):
		with open(club_since_file, 'r+') as f:
			return f.read()
	else:
		return ''

def get_top_id(api, query):
	log_prefix = FILE_NM + ":get_first_id: "
	data = query_twitter_api(api, query, count=1)
	if len(data)==0:
		logging.info(log_prefix + "No data.")
	else:
		return data[0].id_str

def update_since_id(api, club_nm, since_id=""):
	club_since_file = os.path.join(
		constants.SINCE_DIR,
		club_nm.lower().replace(" ", "_") + "_since_id.txt")
	old_id = ""
	if since_id == "":
		old_id = get_top_id(api, query_builder(club_nm))
	if os.path.exists(club_since_file):
		with open(club_since_file, 'r+') as f:
			old_id = f.read()
			f.seek(0)
			f.truncate()
			f.write(since_id)
			f.flush()
	else:
		with open(club_since_file, 'w') as f:
			f.write(since_id).flush()
		old_id = since_id
	return old_id

def qb_name(club_nm):
	if club_nm:
		return '"' + club_nm.replace(' ', '%20') + '"'
	return ''

def qb_hashtags(hashtags):
	if hashtags:
		q = ''
		for hashtag in hashtags.split(', '):
			q += hashtag.replace('#', '%20OR%20%23')
		return q
	return ''

def qb_handle(club_handle):
	if club_handle:
		return '%20OR%20from%3A' + club_handle
	return ''

def qb_exclude(phrases):
	phrases = ['"' + word.replace(' ', '%20') + '"' for word in phrases]
	exclusions = ''
	for phrase in phrases:
		exclusions += '%20-' + phrase
	return exclusions

def query_builder(club_nm):
	query = ""
	with open(constants.CLUBS_JSON) as clubs_json:
		club_data = json.load(clubs_json)[club_nm]

	query += qb_name(club_data["club"])
	query += qb_hashtags(club_data["hashtags"])
	query += qb_handle(club_data["handle"])
	query += qb_exclude(constants.BANNED_PHRASES)
	
	return query

def get_existing_tweets(club_nm, match_ts, collection):
	query = {"club" : club_nm,
				"match_ts" : match_ts}
	results = mongodb.query_collection(collection, query)

	return results


def build_tweet_url(username, msg_id):
	return "https://twitter.com/" + username + "/status/" + msg_id

def build_params(club_nm):
	with open(constants.SECRETS_JSON, 'r') as f:
		secrets = json.load(f)

	consumers = [
		oauth2.Consumer(key=secret["consumer_key"], secret=secret["consumer_secret"])
		for secret in secrets]
	tokens = [
		oauth2.Token(key=secret["access_token"], secret=secret["access_token_secret"])
		for secret in secrets]

	api_params = [{
		"oath_version": "1.0",
		"oauth_nonce": oauth2.generate_nonce(),
		"oauth_timestamp": int(time.time()),
		"lang": "en",
		"oauth_consumer_key": consumer.key,
		"oauth_token": token.key
	} for consumer, token in zip(consumers, tokens)]

	# write data
	club_file = club_nm.lower().replace(" ", "_")

	params_file_nm = os.path.join(constants.PARAMS_DIR, club_file) + "_params.json"
	with open(params_file_nm, 'w') as fp:
		json.dump(api_params, fp)

	consumers_file_nm = os.path.join(constants.CONSUMERS_DIR, club_file) + "_consumers.con"
	with open(consumers_file_nm, 'w') as fc:
		pickle.dump(consumers, fc)

	tokens_file_nm = os.path.join(constants.TOKENS_DIR, club_file) + "_tokens.tok"
	with open(tokens_file_nm, 'w') as ft:
		pickle.dump(tokens, ft)

def authorize_api(index):
	with open(constants.SECRETS_JSON, 'r') as secrets_file:
		secrets = json.load(secrets_file)

	secret = secrets[index]
	consumer_key = secret["consumer_key"]
	consumer_secret = secret["consumer_secret"]
	access_token = secret["access_token"]
	access_token_secret = secret["access_token_secret"]
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	return api

def update_or_save(status, existing_tweets, club_nm, match_ts, iteration, collection):
	status = status._json
	new_tweet = True
	popularity = status["retweet_count"] + status["favorite_count"]
	for tweet in existing_tweets:
		if status["id_str"] == tweet["id_str"]:
			new_tweet = False
			# insert popularity at iteration index, update DB
			popularity_progression = tweet["popularity_progression"]
			popularity_progression[iteration] = popularity
			update_query = {"id_str" : status["id_str"]}
			update_statement = {"popularity_progression" : popularity_progression}
			mongodb.update_one(collection, query = update_query, update=update_statement)
			break

	if new_tweet:
		popularity_progression = [0] * (iteration-1) + \
						[popularity] + \
						[0] * (int(constants.NUM_COLS) - iteration)

		record = {"id_str" : status["id_str"],
					"club" : club_nm,
					"match_ts" : match_ts,
					"popularity_progression" : popularity_progression}
		mongodb.insert_object(collection, record)

def analyze_text(text):
	APPLICATION_ID = '' # application id
	APPLICATION_KEY = '' # application key
	parameters = {"text": text}
	url = 'https://api.aylien.com/api/v1/sentiment'
	headers = {
		"Accept": "application/json",
		"Content-type": "application/x-www-form-urlencoded",
		"X-AYLIEN-TextAPI-Application-ID": APPLICATION_ID,
		"X-AYLIEN-TextAPI-Application-Key": APPLICATION_KEY
  	}
	opener = urllib2.build_opener()
	request = urllib2.Request(url, urllib.urlencode(parameters), headers)
	response = opener.open(request);
	return json.loads(response.read())

# must have count and/or since id, cannot be called with neither or will hit rate limit
def query_twitter_api(
	api,
	query,
	count=None,
	result_type='mixed',
	max_id="",
	since_id=""):

	results = [status for status in tweepy.Cursor(api.search, 
		q=query, 
		since_id=since_id,
		max_id=max_id,
		result_type=result_type).items(count)]
	return results


def get_tweets_for_match(club_nm, match_ts):
	print ''

def within(num, min, max):
	return min <= num <= max

def get_match_start_and_end(match):
	match_ts = match["timestamp"]
	match_end = match_ts + 60 * 60 * 2
	return (match_ts, match_end)

def utc2snowflake(stamp):
    return (int(round(stamp * 1000)) - 1288834974657) << 22

def snowflake2utc(sf):
    return ((sf >> 22) + 1288834974657) / 1000.0

def get_team_tweets(api_index, start_timestamp, end_timestamp, club_nm, count, tweets):
	if end_timestamp == start_timestamp:
		return api_index, tweets
	if api_index == 0:
		print "Currently at ", time.time()
		print "Sleeping for ", 16 * 60
		time.sleep(16 * 60)
	api = authorize_api(api_index)
	print start_timestamp, end_timestamp
	query = query_builder(club_nm)
	since_id = utc2snowflake(start_timestamp)
	max_id = utc2snowflake(end_timestamp)
	new_tweets = query_twitter_api(
		api=api,
		query=query,
		since_id=since_id,
		max_id=max_id,
		count=count)
	if len(new_tweets) == 0:
		return api_index, tweets
	# print new_tweets[0]._json["created_at"], new_tweets[-1]._json["created_at"]
	first_timestamp = mongodb.twitter_time_to_unix(new_tweets[-1]._json["created_at"])
	return get_team_tweets((api_index + 1) % constants.NUM_SECRETS, start_timestamp, first_timestamp, club_nm, count, tweets + new_tweets)

def build_document(status, team, match_ts):

		# add tweet's unix ts, the match date, and team to tweet object
		tweet["unix_ts"] = mongodb.twitter_time_to_unix(tweet["created_at"])
		tweet["team"] = team
		tweet["match_ts"] = match_ts
		
		return tweet

def populate_popularity(club_nm, since_id="", iteration=1, match_ts=time.time()):

	log_prefix = FILE_NM + ":populate_popularity: "

	# build api object using secrets
	with open(constants.SECRETS_JSON, 'r') as secrets_file:
		secrets = json.load(secrets_file)

	secrets_index = iteration % constants.NUM_SECRETS
	api = authorize_api(secrets_index)

	# open db connection
	collection = mongodb.init_collection('popular')
	existing_tweets = get_existing_tweets(club_nm, match_ts, collection)

	query = query_builder(club_nm)
	new_tweets = query_twitter_api(
		api,
		query,
		result_type=constants.TWEET_TYPE,
		since_id=since_id)

	if len(new_tweets) == 0:
		logging.info(log_prefix + 'no tweets now')
	else:
		for status in new_tweets:
			update_or_save(status, existing_tweets, club_nm, match_ts, iteration, collection)

if __name__ == '__main__':
	api_index = 1
	query = query_builder("Bournemouth")

	matches_collection = mongodb.init_collection('matches')
	now = time.time()
	two_weeks_ago = now - 60 * 60 * 24 * 7 * 2
	matches_query = {"timestamp" : {"$gt": two_weeks_ago}}
	matches = mongodb.query_collection(matches_collection, matches_query)
	live_collection = mongodb.init_collection('live')
	for m in matches:
		print m
		start, end = get_match_start_and_end(m)
		home, away, match_ts = m["home"], m["away"], m["timestamp"]
		home_query = {"team": home, "match_ts":match_ts}
		away_query = {"team": away, "match_ts":match_ts}
		home_tweets = mongodb.query_collection(live_collection, home_query)
		away_tweets = mongodb.query_collection(live_collection, away_query)
		for t in home_tweets + away_tweets:
			del(t["_id"])
		home_filename = constants.DATA_DIR + "migration/" + home.lower().replace(" ", "-") + "-" + str(match_ts) + ".json"
		away_filename = constants.DATA_DIR + "migration/" + away.lower().replace(" ", "-") + "-" + str(match_ts) + ".json"
		print home_filename
		with open(home_filename, 'w') as f:
			json.dump(home_tweets, f)
		with open(away_filename, 'w') as f:
			json.dump(away_tweets, f)

	# 	m_start_id, m_end_id = utc2snowflake(start), utc2snowflake(end)
	# 	home_query = query_builder(home)
	# 	away_query = query_builder(away)
	# 	print 'getting home'
	# 	api_index, home_tweets = get_team_tweets(api_index, start, end, home, 1000, [])
	# 	api_index += 1
	# 	print 'getting away'
	# 	api_index, away_tweets = get_team_tweets(api_index, start, end, away, 1000, [])
	# 	api_index += 1
	# 	# away_tweets = query_twitter_api(
	# 	# 	api=api,
	# 	# 	query=away_query, 
	# 	# 	since_id=m_start_id,
	# 	# 	max_id=m_end_id,
	# 	# 	count=1000)
	# 	print len(home_tweets)
	# 	for t in home_tweets:
	# 		tweet = t._json
	# 		tweet_user = tweet["user"]["id_str"]
	# 		tweet_text = tweet['text']
	# 		tweet_id = tweet["id_str"]
	# 		document = build_document(tweet, home, start)
	# 		existing_tweet = mongodb.query_collection(live_collection, {"id": tweet_id})
	# 		if existing_tweet:
	# 			mongodb.update_one(live_collection, {"id": tweet_id}, document)
	# 		else:
	# 			mongodb.insert_object(live_collection, document)
	# 	for t in away_tweets:
	# 		tweet = t._json
	# 		tweet_user = tweet["user"]["id_str"]
	# 		tweet_text = tweet['text']
	# 		tweet_id = tweet["id_str"]
	# 		document = build_document(tweet, away, start)
	# 		existing_tweet = mongodb.query_collection(live_collection, {"id": tweet_id})
	# 		if existing_tweet:
	# 			mongodb.update_one(live_collection, {"id": tweet_id}, document)
	# 		else:
	# 			mongodb.insert_object(live_collection, document)

	# 	#print m_start_id, m_end_id