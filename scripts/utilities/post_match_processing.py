import csv
import datetime
import requests
import operator
import os, sys
import time
import logging
from bs4 import BeautifulSoup

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))

resources_path = os.path.abspath(os.path.join(BASE_DIR, 'resources'))
sys.path.append(resources_path)
import constants

sys.path.append(constants.UTILITIES_DIR)
import mongo_utilities as mongodb

# initiate logging
logging.basicConfig(filename=constants.LOG_FILE, 
						level=constants.LOG_LEVEL,
						format=constants.LOG_FORMAT)

FILE_NM = "post_match_processing"

def get_tweets_for_match(match):
	collection = mongodb.init_collection('live')
	query = {"match_ts" : match["timestamp"], 
		"$or": [{"team" : match["home"]},
				{"team" : match["away"]}
				]}
	sort = ("unix_ts", 1)
	print 'getting tweets'
	print query
	result = mongodb.query_collection(collection, query, sort)
	return result

def scrape_score(match):
	log_prefix = FILE_NM + ":scrape_score: "
	month = datetime.datetime.fromtimestamp(match["timestamp"]).month
	if month in [6, 7]:
		logging.error(log_prefix + "There's no match data during summer, attempting to find score for %s vs %s on %d" % (match["home"], match["away"], match["timestamp"]))
		return ''
	url = "http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=" + str(month)

	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")

	#third table on page lists matches
	games_table = soup.find_all('table')[2]

	match_day_list = []
	match_day = []
	for elt in games_table.contents:
		if match_day:
			match_day += [elt]
		if 'shsTableTtlRow' in str(elt):
			match_day = [elt]
			if match_day:
				match_day_list += [match_day]

	matches = []
	for md in match_day_list:
		for elt in md:
			if "shsRow0Row" in str(elt) or "shsRow1Row" in str(elt):
				if not (match["home"] == elt.find_all('td', {"class":"shsNamD"})[1].text
					and match["away"] == elt.find_all('td', {"class":"shsNamD"})[2].text):
					continue
				else:
					score = elt.find_all('td', {"class":"shsNamD"})[0].text
	return score


def chunks(start, end, chunk_size):
	chunks = []
	while(start < end):
		chunks += [start]
		start += chunk_size
	chunks += [end]
	
	return chunks


'''
accepts set of tweets sorted ascending by timestamp
returns list of counts of tweets per minute
'''
def get_counts_for_match(tweets, match):
	match_start = int(match["timestamp"])
	match_end = match_start + constants.TOT_MINUTES * 60

	curr_tweet_index = 0

	ts_chunks = chunks(match_start, match_end, 60)
	
	# intialize lists of 0s for counts for t1, t2
	t1_counts = [0] * (len(ts_chunks) - 1)
	t2_counts = [0] * (len(ts_chunks) - 1)
	for i in xrange(len(ts_chunks)-1):
		start = ts_chunks[i]
		end = ts_chunks[i+1]
		while(curr_tweet_index < len(tweets) 
			and tweets[curr_tweet_index]["unix_ts"] < end
			and tweets[curr_tweet_index]["unix_ts"] >= start):
			if tweets[curr_tweet_index]["team"] == match["home"]:
				t1_counts[i] += 1
			if tweets[curr_tweet_index]["team"] == match["away"]:
				t2_counts[i] += 1
			curr_tweet_index += 1
	counts = {"home" : {"counts": t1_counts},
				"away" : {"counts": t2_counts}
			}

	return counts

def find_popular_tweets(num_tweets, tweets):
	all_tweets = {}
	for t in tweets:
		popularity = t["retweet_count"] + t["favorite_count"]
		all_tweets[t["id_str"]] = popularity

	sorted_popular_tweets = [key for key in sorted(all_tweets, key=all_tweets.get, reverse=True)[:num_tweets]]

	return sorted_popular_tweets

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
	all_hashtags = {}
	for tweet in tweets:
		for hashtag in tweet["entities"]["hashtags"]:
			hashtag_text = hashtag["text"].encode('utf8')
			if hashtag_text in all_hashtags:
				all_hashtags[hashtag_text] += 1
			else:
				all_hashtags[hashtag_text] = 1
		
	sorted_top_hashtags = [(key, all_hashtags[key]) for key in sorted(all_hashtags, key=all_hashtags.get, reverse=True)[:num_hashtags*5]]
	print sorted_top_hashtags
	
	# remove duplicates from cases
	unique_top_hashtags = {}
	for h in sorted_top_hashtags:
		hashtag = h[0]
		count = h[1]
		if hashtag.lower() in unique_top_hashtags:
			unique_top_hashtags[hashtag.lower()] += count
		else:
			unique_top_hashtags[hashtag.lower()] = count

	sorted_unique_top_hashtags = [[key, unique_top_hashtags[key]] for key in sorted(unique_top_hashtags, key=unique_top_hashtags.get, reverse=True)]

	#restore original cases
	for index, lower_h in enumerate(sorted_unique_top_hashtags):
		for h in sorted_top_hashtags:
			if lower_h[0] == h[0].lower():
				sorted_unique_top_hashtags[index][0] = h[0]
				break

	top_hashtags = []
	for index, hashtag in enumerate(sorted_unique_top_hashtags[:num_hashtags]):
		hashtag_dict = {"rank": index+1,
						"text": hashtag[0],
						"count": hashtag[1]}
		top_hashtags += [hashtag_dict]

	return top_hashtags 


def process_match(match):
	tweets = get_tweets_for_match(match)
	print len(tweets)
	score = scrape_score(match)
	counts = get_counts_for_match(tweets, match)
	top_hashtags = find_top_hashtags(5, tweets)
	top_tweets = find_popular_tweets(10, tweets)
	post_processing = {"home" : match["home"],
						"away" : match["away"],
						"timestamp" : match["timestamp"],
						"score" : score,
						"counts" : counts,
						"top_hashtags" : top_hashtags,
						"top_tweets" : top_tweets}

	return post_processing

def main():
	matches_collection = mongodb.init_collection('matches')
	matches = mongodb.query_collection(matches_collection)
	for m in matches[-1:]:
		#post_processing = process_match(m)
		tweets = get_tweets_for_match(m)
		top_hashtags = find_top_hashtags(5, tweets)


if __name__ == '__main__':
	main()


