from bs4 import BeautifulSoup
import requests
import os
import datetime

def get_match_data(url, dest, weeks=1):
	r = requests.get(url)

	soup = BeautifulSoup(r.content)

	# only collect data for certain number of weeks
	date_limit = (datetime.datetime.now() + datetime.timedelta(days=7*weeks)).strftime("%d %B %Y")

	#third table on page lists matches
	games_table = soup.find_all('table')[3]

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
			if "shsTableTtlRow" in str(elt):
				# dates appear in Saturday, 19 December 2015 format
				# cut out weekday
				date = elt.text[elt.text.find(' ')+1:]
				if date > date_limit:
					break
			elif "shsRow0Row" in str(elt) or "shsRow1Row" in str(elt):
				time = elt.find_all('span', {"class":"shsCTZone"})[0].text
				home = elt.find_all('td', {"class":"shsNamD"})[1].text
				away = elt.find_all('td', {"class":"shsNamD"})[2].text
				matches += [[date, time, home, away]]

	with open(dest + 'matches_' + datetime.datetime.now().strftime("%m-%d-%Y") + '.txt', 'a') as f:
		for m in matches:
			for index, field in enumerate(m):
				# if index == len(m):
				# 	f.write(field)
				# else:
				f.write(field + ", ")
			f.write("\n")
	
if __name__ == '__main__':
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
	month = datetime.datetime.now().month
	if month in [6, 7]:
		print "it's June dum dum, there's no football happening"
		exit()
	url = "http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=" + str(month)
	get_match_data(url, os.path.join(BASE_DIR, '/data/matches/'))




