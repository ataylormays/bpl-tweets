import csv
import json
import oauth2
import os
import pickle
import sys
import time
import urllib
import urllib2

resources_path = os.path.abspath(os.path.join('../../..', 'resources'))
sys.path.append(resources_path)

import constants

def convert_datetime(twitter_date):
	old_fmt = '%a %b %d %H:%M:%S +0000 %Y'
	new_fmt = '%Y-%m-%d %H:%M:%S'
	d = time.strptime(twitter_date, old_fmt)
	return time.strftime(new_fmt, d)

def get_hashtags(club_nm):
	with open(constants.CLUBS_FILE) as clubs_file:
		clubs = csv.reader(clubs_file, delimiter=",")
		for row in clubs:
			if(row[0]) == club_nm:
				print row[1].split(", ")

def extract_hashtags(twitter_object):
	if len(twitter_object) == 0:
		return ""
	else:
		h_tags = twitter_object[0]["text"]
		for h in twitter_object[1:]:
			h_tags += ", " + h["text"]
		return h_tags

def get_since_id(club_nm):
	club_since_file = os.path.join(
		constants.SINCE_DIR,
		club_nm.lower().replace(" ", "_") + "_since_id.txt")
	if os.path.exists(club_since_file):
		with open(club_since_file, 'r+') as f:
			return f.read()
	else:
		return ''

def get_top_id(query):
	data = query_twitter_api(query)
	if data["statuses"] == []:
		print "no data"
	else:
		return data["statuses"][0]["id_str"]

def update_since_id(club_nm, since_id=""):
	club_since_file = os.path.join(
		constants.SINCE_DIR,
		club_nm.lower().replace(" ", "_") + "_since_id.txt")
	old_id = ""
	if since_id == "":
		old_id = get_top_id(query_builder(club_nm))
	if os.path.exists(club_since_file):
		with open(club_since_file, 'r+') as f:
			old_id = f.read()
			f.seek(0)
			f.truncate()
			f.write(since_id)
	else:
		with open(club_since_file, 'w') as f:
			f.write(since_id)
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

def build_tweet_url(username, msg_id):
	return "https://twitter.com/" + username + "/status/" + msg_id

def build_params():
	with open(constants.SECRETS_FILE, 'r+') as f:
		rows = csv.reader(f)
		secrets = [row for row in rows]

	consumers = [
		oauth2.Consumer(key=secret[0], secret=secret[1])
		for secret in secrets]
	tokens = [
		oauth2.Token(key=secret[2], secret=secret[3])
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
	with open(constants.PARAMS_FILE, 'w') as fp:
		json.dump(api_params, fp)

	with open(constants.CONSUMERS_FILE, 'w') as fc:
		pickle.dump(consumers, fc)

	with open(constants.TOKENS_FILE, 'w') as ft:
		pickle.dump(tokens, ft)

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

def query_twitter_api(
	query,
	count=1,
	since_id="",
	max_id="",
	result_type="",
	index=0):
	# read in data
	with open(constants.PARAMS_FILE, 'r+') as fp:
		api_params = json.load(fp)

	with open(constants.TOKENS_FILE, 'r+') as ft:
		# rows = csv.reader(f)
		# tokens = [row for row in rows]
		tokens = pickle.load(ft)

	with open(constants.CONSUMERS_FILE, 'r+') as fc:
		# rows = csv.reader(f)
		# consumers = [row for row in rows]
		consumers = pickle.load(fc)

	params = api_params[index]
	url = constants.RESOURCE_URL
	params["q"] = query
	params["count"] = count # number of tweets per page
	params["since_id"] = since_id # returns tweets more recent than
	params["max_id"] = max_id # returns tweets older than
	params["result_type"] = result_type # popular, recent, mixed
	req = oauth2.Request(method="GET", url=url, parameters=params)
	signature_method = oauth2.SignatureMethod_HMAC_SHA1()
	req.sign_request(signature_method, consumers[index], tokens[index])
	headers = req.to_header()
	url = req.to_url()
	response = urllib2.Request(url)
	return json.load(urllib2.urlopen(response))

def populate_popularity(club_nm, since_id="", iteration=1):
	#build api_params
	build_params()

	tot_time_start = time.time()
	if since_id == "":
		since_id = update_since_id(club_nm)
	i = 0
	query = query_builder(club_nm)
	prev_id = get_top_id(query)
	collected_tweets = set()
	index = 0
	all_data = []
	tweet_data = []

	#read and edit data
	input_file_nm = os.path.join(
		constants.POPULARITY_DIR,
		club_nm.lower().replace(' ', '_') + "_popularity.csv")
	try:
		with open(input_file_nm, 'rU') as f:
			tweet_file = csv.reader(f, delimiter=",")
			tweet_data = [row for row in tweet_file]
	except:
		tweet_data = []

	# breaks when no more data
	while(True):
		# if program has been running for > 45 minutes, get new tokens
		if time.time() - tot_time_start > constants.REFRESH_TIME:
			build_params()

		start = time.time()
		data = query_twitter_api(
			query,
			count=100,
			max_id=prev_id,
			since_id=since_id,
			index=index,
			result_type=constants.TWEET_TYPE)

		if data["statuses"] == []:
			print "end of data"
			break
		else:
			prev_id = int(data["statuses"][-1]["id"])-1
			i += 1
			# empty tweet_data variable after first run
			if i != 1:
				tweet_data = []
			print str(len(data["statuses"])) + " on this page"
			for status in data["statuses"]:
				id_str =  status["id_str"]
				if id_str in collected_tweets:
					continue
				else:
					collected_tweets.add(id_str)

				popularity = str(
					status["retweet_count"] + \
					status["favorite_count"])
				new_tweet = True
				for row in tweet_data:
					if(row[0] == id_str):
						print 'amending existing tweet'
						row[iteration] = popularity
						new_tweet = False
						break
				if new_tweet:
					content = [id_str] + \
						["0"] * (iteration-1) + \
						[str(popularity)] + \
						["0"] * \
						(
							int(
							constants.NUM_COLS) - \
							iteration)
					tweet_data += [content]

		all_data += tweet_data
		end = time.time()
		print i, end-start
		index += 1
		index = index % 10

	#write data (overwrites file)
	with open(input_file_nm, 'w+') as f:
		csv.writer(f, delimiter=",").writerows(all_data)
