import csv
import datetime
import requests
import operator
import os, sys
import time
from bs4 import BeautifulSoup

file_loc = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))

resources_path = os.path.abspath(os.path.join(BASE_DIR, 'resources'))
sys.path.append(resources_path)
import constants

sys.path.append(constants.UTILITIES_DIR)
import mongo_utilities as mongodb

def get_matches(match_ts):
	matches_filename = os.path.join(constants.MATCHES_DIR, "matches.csv")
	matches = []
	with open(matches_filename, "r") as f:
		matches_reader = csv.reader(f, delimiter=",")
		for row in matches_reader:
			match = {"date" : row[0],
				"time" : row[1],
				"timestamp" : row[2], 
				"home" : row[3], 
				"away" : row[4]
			}
			matches += [match]

	return matches

def get_tweets_for_match(match):
	collection = mongodb.init_collection('live')
	query = {"match_ts" : match["timestamp"], 
		"$or": [{"team" : match["home"]},
				{"team" : match["away"]}
				]}
	sort = ("unix_ts", 1)
	result = mongodb.query_collection(collection, query, sort)
	return result

def scrape_score(match):
	month = datetime.datetime.now().month
	if month in [6, 7]:
		print "it's summer dum dum, there's no football happening"
		sys.exit()
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
	t1_counts = [0] * len(ts_chunks)
	t2_counts = [0] * len(ts_chunks)
	for i in xrange(len(ts_chunks)-1):
		start = ts_chunks[i]
		end = ts_chunks[i+1]
		while(tweets[curr_tweet_index]["unix_ts"] < end
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
			if hashtag in all_hashtags:
				all_hashtags[hashtag] += 1
			else:
				all_hashtags[hashtags] = 1

	sorted_top_hashtags = sorted(all_hashtags.items(), key=operator.itemgetter(0))

	top_hashtags = []
	for index, hashtag in enumerate(sorted_top_hashtags):
		hashtag_dict = {"rank": index+1,
						"text": hashtag[0],
						"count": hashtag[1]}
		top_hashtags += [hashtag_dict]

	return top_hashtags 


def process_match(match):
	tweets = get_tweets_for_match(match)
	score = scrape_score(match)
	counts = get_counts_for_match(tweets, match)
	top_hashtags = find_top_hashtags(5, tweets)
	post_processing = {"home" : match["home"],
						"away" : match["away"],
						"timestamp" : match["timestamp"],
						"score" : score,
						"counts" : counts,
						"top_hashtags" : top_hashtags}

	return post_processing

def main():
	matches = get_matches()
	for m in matches:
		post_processing = process_match(m)


if __name__ == '__main__':
	main()


