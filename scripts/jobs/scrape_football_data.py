#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import os, sys
import datetime
import csv
import traceback

resources_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources')
sys.path.append(resources_path)
import constants

def scrape_match_data(url, dest, weeks=1):
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
				time = elt.find_all('span', {"class":"shsCTZone"})[0].text.replace(" CT", "")
				home = elt.find_all('td', {"class":"shsNamD"})[1].text
				away = elt.find_all('td', {"class":"shsNamD"})[2].text
				matches += [[date, time, home, away]]

	with open(dest + 'matches.csv', 'w') as f:
		csv.writer(f, delimiter=",").writerows(matches)
	
if __name__ == '__main__':
	# print constants.MATCHES_DIR
	month = datetime.datetime.now().month
	if month in [6, 7]:
		print "it's summer dum dum, there's no football happening"
		sys.exit()
	url = "http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=" + str(month)
	try:
		scrape_match_data(url, constants.MATCHES_DIR)
	except:
		print "Error in scraping football data from %s" % url
		traceback.print_exc()




