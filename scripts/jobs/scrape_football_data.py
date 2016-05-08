#!/usr/local/lib/python2.7.10/bin//python

from bs4 import BeautifulSoup
import requests
import os, sys
import datetime, time, calendar
import traceback

file_loc = os.path.abspath(__file__)
resources_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(file_loc))), 'resources')
sys.path.append(resources_path)
import constants

sys.path.append(constants.UTILITIES_DIR)
import mongo_utilities as mongo

def datetime2timestamp(match_dt):

	# sample dt: 17 January 2016 10:15 AM
	match_dt_format = "%d %B %Y %H:%M"
	t = time.strptime(match_dt, match_dt_format)
	match_ts = calendar.timegm(t)

	return match_ts

def scrape_match_data(urls, collection, weeks=2):
	r = requests.get(url)

	soup = BeautifulSoup(r.content, "html.parser")

	# only collect data for certain number of weeks
	date_limit = (datetime.datetime.now() + datetime.timedelta(days=7*weeks)).strftime("%d %B %Y")
	date_limit = datetime.datetime.strptime(date_limit, "%d %B %Y")

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
		# dates appear in Saturday, 19 December 2015 format
		# cut out weekday
		date = md[0].text[md[0].text.find(' ')+1:]
		# skip over dates in past
		# stop once program reaches dates in future
		if datetime.datetime.strptime(date, "%d %B %Y") > date_limit:
			break
		if datetime.datetime.strptime(date, "%d %B %Y") < datetime.datetime.now():
			continue	
		for elt in md:
			if "shsRow0Row" in str(elt) or "shsRow1Row" in str(elt):
				try:
					time = elt.find_all('span', {"class":"shsGMTZone"})[0].text.replace(" GMT", "")
					home = elt.find_all('td', {"class":"shsNamD"})[1].text
					away = elt.find_all('td', {"class":"shsNamD"})[2].text
					match_ts = datetime2timestamp(date + " " + time)
					matches += [[date, time, match_ts, home, away]]
				except Exception, e:
					print 'Failed on row'
					print elt
        
        flag = False
        for match in matches:
                date = match[0]
                human_time = match[1]
                time = match[2]
                home = match[3]
                away = match[4]
                match_dict = { "timestamp" : time,
                               "home" : home,
                               "away" : away,
                               "human_time" : human_time,
                               "date" : date }
                query = { "timestamp" : time,
                          "home" : home,
                          "away" : away }
                results = mongo.query_collection(collection, query)
                if not results:
                        mongo.insert_object(collection, match_dict)
                else:
                        mongo.update_one(collection, query, match_dict)

if __name__ == '__main__':
	# print constants.MATCHES_DIR
	month = datetime.datetime.now().month
	if month in [6, 7]:
		print "it's summer dum dum, there's no football happening"
		sys.exit()
	urls = [
                "http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=" + str(month),
                "http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=" + str((month + 1) % 12) ]
	try:
                collection = mongo.init_collection('matches')
                for url in urls:
                        scrape_match_data(url, collection)
	except:
		print "Error in scraping football data from %s" % url
		traceback.print_exc()




