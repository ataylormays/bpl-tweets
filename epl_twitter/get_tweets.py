import oauth2
import time
import urllib2
import json
import csv
from django.conf import settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epl_twitter.settings")
settings.configure(
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3',
	        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	    }
	},

    )
import django
from tweets.models import Tweet

main_dir = "C:/Users/ataylor/Documents/Projects/web apps/epl twitter"

clubs_file_nm = main_dir + "/data/twitter_clubs.csv"

REFRESH_TIME = 45 * 60

resource_url = "https://api.twitter.com/1.1/search/tweets.json"

banned_phrases=[
	"RT",
	"PRE ORDER",
	"PRE-ORDER"
]

def convert_datetime(twitter_date):
	old_fmt = '%a %b %d %H:%M:%S +0000 %Y'
	new_fmt = '%Y-%m-%d %H:%M:%S'
	d = time.strptime(twitter_date, old_fmt)
	return time.strftime(new_fmt, d)


def get_hashtags(club_nm):
	with open(clubs_file_nm) as clubs_file:
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

def update_since_id_file(club_nm, since_id):
	club_file_nm = main_dir + "/data/" + club_nm.lower().replace(" ", "_") + "_since_id.txt"
	old_id = ""
	if os.path.exists(club_file_nm):
		with open(club_file_nm, 'r+') as f:
			old_id = f.read()
			f.seek(0)
			f.truncate()
			f.write(since_id)
	else:
		with open(club_file_nm, 'w') as f:
			old_id = ''
			f.write(since_id)
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

def query_bulider(club_nm):
	query = ""
	with open(clubs_file_nm) as clubs_file:
		clubs = csv.reader(clubs_file, delimiter=",")
		for row in clubs:
			if(row[0]) == club_nm:
				query += qb_name(row[0])
				query += qb_hashtags(row[1]) 
				query += qb_handle(row[2])
		query += qb_exclude(banned_phrases)
		return query

def build_tweet_url(username, msg_id):
	return "https://twitter.com/" + username + "/status/" + msg_id

api_params = [{}]
consumers = []
tokens = []
def build_params():
	global consumers
	global tokens
	global api_params

	secret_file = main_dir + "/data/secrets.csv"

	with open(secret_file, 'r+') as f:
		rows = csv.reader(f)
		secrets = [row for row in rows]
	
	consumers = [oauth2.Consumer(key=secret[0], secret=secret[1]) for secret in secrets]
	tokens = [oauth2.Token(key=secret[2], secret=secret[3]) for secret in secrets] 

	api_params = [{
		"oath_version": "1.0",
		"oauth_nonce": oauth2.generate_nonce(),
		"oauth_timestamp": int(time.time()),
		"lang": "en",
		"oauth_consumer_key": consumer.key,
		"oauth_token": token.key
	} for consumer, token in zip(consumers, tokens)]

def query_twitter_api(query, count=1, since_id="", max_id="", result_type="", index=0):
	params = api_params[index]
	url = resource_url
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


def get_top_id(query):
	data = query_twitter_api(query)
	if data["statuses"] == []:
		print "end of data"
	else:
		return int(data["statuses"][0]["id"])
		 
def get_historic_tweets(club_nm):
	print club_nm
	#build api_params 
	build_params()

	tot_time_start = time.time()
	query = query_bulider(club_nm)
	top_id = str(get_top_id(query))
	last_id = update_since_id_file(club_nm, top_id)
	prev_id = top_id
	i = 0
	advance = True
	collected_tweets = set()
	index = 0
	while(advance):
		# if program has been running for > 45 minutes, get new tokens
		if time.time() - tot_time_start > REFRESH_TIME:
			build_params()

		start = time.time()
		data = query_twitter_api(query, count=100, max_id=prev_id, since_id=last_id, index=index, result_type="popular")
		if data["statuses"] == []:
			print "end of data"
			advance = False
		else:
			prev_id = int(data["statuses"][-1]["id"])-1
			i += 1
			for status in data["statuses"]:
				txt =  status["text"].encode('utf-8')
				if txt in collected_tweets:
					continue
				else:
					collected_tweets.add(txt)
				c =  convert_datetime(status["created_at"])
				f_ct = status["favorite_count"]
				id_str = status["id_str"]
				rt_ct = status["retweet_count"]
				h_tags = extract_hashtags(status["entities"]["hashtags"])
				is_rt = True if "retweeted_status" in status.keys() else False
				url = build_tweet_url(status["user"]["screen_name"], id_str)
				t = Tweet(created=c, url=url, team=club_nm, favorites=f_ct, tweet_id=id_str, retweets=rt_ct, text=txt,hashtags=h_tags, is_retweet=is_rt)
				t.save()
			end = time.time()
			print i, end-start
			index += 1
			index = index % 10

if __name__ == "__main__":
	with open(clubs_file_nm) as clubs_file:
		clubs = csv.reader(clubs_file, delimiter=",")
		#skip header row
		next(clubs)
		for row in clubs:
			get_historic_tweets(row[0])