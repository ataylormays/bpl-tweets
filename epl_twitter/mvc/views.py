from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.module_loading import import_string
from dateutil.relativedelta import relativedelta
from .models import Tweet
import csv
import json
from forms import DatesForm
import datetime
import time
import os, sys
import collections

path = os.path.abspath(os.path.join('..', 'resources'))
sys.path.append(path)

try:
	import constants
except ImportError, e:
	print 'import constants failed'
	print 'sys_path: ', sys.path
	constants = __import__('constants')
	print 'constants: %r' % constants
	try:
		print (
			'constants is at %s (%s)' %
			(constants.__file__, constants.__path__))
	except Exception, e:
		print 'Cannot give details on constants (%s)' % e

sys.path.append(constants.UTILITIES_DIR)
import mongo_utilities as mongo

def count_elts(numbers, limit):
	output = {}
	for n in numbers:
		if n in output.keys():
			output[n] += 1
		else:
			output[n] = 1
	return sorted(output.items(), key=lambda x:-1*x[1])[:limit]

def create_match_url(team1, team2, timestamp, page_type):
	t1, t2 = (
		team1.lower().replace(' ', '_'),
		team2.lower().replace(' ', '_'))
	if page_type == 'live':
		url = '/live/'
	elif page_type == 'archive':
		url = '/archive/'
	url += t1 + '-' + t2 + '-' + str(timestamp)
	return url

# create sorted list between two dates with placeholders for counts of sentiment
# sentiment: [positive, neutral, negative]
# elt of L: [date, sentiment] eg [date, [positive, neutral, negative]]
def create_sent_list(dt1, dt2):
	L = []
	while(dt1 < dt2):
		# store dates as 2015-06-12, same as DB
		formatted_dt = dt1.strftime("%Y-%m-%d")
		L.append([formatted_dt, [0, 0, 0]])
		dt1 += datetime.timedelta(days=1)
	return L

# returns dict of (date: index) for sorted dates b/w dt1 & dt2
# meant for easy access of sent_list
def create_date_dict(dt1, dt2):
	d = {}
	i = 0
	while(dt1 < dt2):
		# store dates as 2015-06-12, same as DB
		formatted_dt = dt1.strftime("%Y-%m-%d")
		d[formatted_dt] = i
		dt1 += datetime.timedelta(days=1)
		i += 1
	return d

def count_sentiments(tweets, dt1, dt2):
	sents = create_sent_list(dt1, dt2)
	dates = create_date_dict(dt1, dt2)
	for t in tweets:
		formatted_dt = t.created.strftime("%Y-%m-%d")
		index = dates[formatted_dt]
		if t.sentiment == 'positive':
			sents[index][1][0] += 1
		elif t.sentiment == 'neutral':
			sents[index][1][1] += 1
		else:
			sents[index][1][2] += 1
	return sents

# compute percentages of each sentiment
# creates sorted list between two dates with placeholders for counts
#of sentiment
# sentiment: [% pos, % neut, % neg]
# returns list L where elt of L: is of the form [date, sentiment],
# e.g. [date, [% pos, % neut, % neg]]
def sentiment_percs(dt1, dt2, sent_list):
	L = []
	date_list = [elt[0] for elt in sent_list]
	date_dict = create_date_dict(dt1, dt2)
	for date in date_list:
		index = date_dict[date]
		sent_total = float(sum(sent_list[index][1]))
		if sent_total == 0:
			L.append([date, [0, 0, 0]])
		else:
			sentiments = sent_list[index][1]
			L.append([
				date,
				[round(100*sentiments[0]/sent_total, 2),
				round(100*sentiments[1]/sent_total, 2),
				round(100*sentiments[2]/sent_total, 2)]])
	return L

def get_club_names():
	clubs_file_nm = constants.CLUBS_JSON
	with open(clubs_file_nm) as clubs_file:
		club_names = []
		clubs = clubs_file.read()
		clubs = json.loads(clubs)
		for name in sorted(clubs.keys()):
			club_names.extend(
				[(name.replace(' ', '_').lower(), name)])
	return club_names

def format_match_dt_from_db(date_string):
	dt = datetime.datetime.strptime(date_string, "%d %B %Y")
	formatted_date_string = datetime.datetime.strftime(dt, "%B %d %Y").lstrip("0").replace(" 0", " ")
	return formatted_date_string

def placeholder(request):
	template = loader.get_template('placeholder.html')
	context = RequestContext(request)

	return HttpResponse(template.render(context))

def about(request):
	today = datetime.date.today().strftime("%B %d, %Y").lstrip("0").replace(" 0", " ")
	template = loader.get_template('about.html')
	context = RequestContext(request, {
		'today': today,
		})

	return HttpResponse(template.render(context))

def matches(request):
	today = datetime.date.today()
	matches = {}
	collection = mongo.init_collection('matches')
	matches_by_date = []
	# get (in order) today, upcoming, yesterdays matches 
	for i in [0, 1, 2, 3, 4, 5, 6, 7, -1]:
		date = (today + datetime.timedelta(days=i)).strftime("%-d %B %Y")
		results = mongo.query_collection(collection, {"date" : date})

		matches_on_date = []
		for match in results:
			delta = datetime.timedelta(minutes=constants.TOT_MINUTES)
			now = datetime.datetime.now()
			crest1 = os.path.join(
				'club-crests',
				match['home'].lower().replace(' ', '_') + '-crest.png')
			crest2 = os.path.join(
				'club-crests',
				match['away'].lower().replace(' ', '_') + '-crest.png')

			start = datetime.datetime.fromtimestamp(float(match['timestamp']))
			date_string = match['date']
			state = 'LIVE'
			if now < start:
				state = '(upcoming)'
			elif now > start + delta:
				state = 'FT'
			url = create_match_url(match['home'], match['away'], match['timestamp'], 'live')
			match_data = { "date" :  match['date'],
							"time" : match['human_time'],
							"timestamp" : match['timestamp'],
							"home" : match['home'],
							"away" : match['away'],
							"state" : state,
							"home_crest" : crest1,
							"away_crest" : crest2,
							"dest_url" : url }
			matches_on_date += [match_data]
		matches_by_date += [matches_on_date]

	template = loader.get_template('matches.html')
	context = RequestContext(request, {
				'matches': matches_by_date
				})

	return HttpResponse(template.render(context))


def live(request, team1, team2, timestamp):
	template = loader.get_template('live.html')
	context = RequestContext(request, {
		'team1Title': team1.title().replace('_', ' '),
		'team2Title': team2.title().replace('_', ' '),
		'team1': team1,
		'team2': team2,
		'timestamp': timestamp,
	})
	return HttpResponse(template.render(context))

def teams(request):
	club_names = get_club_names()

	template = loader.get_template('teams.html')
	context = RequestContext(request, {
		'club_names': club_names,
		})
	return HttpResponse(template.render(context))

def contact(request):
	template = loader.get_template('contact.html')
	context = RequestContext(request)

	return HttpResponse(template.render(context))

def group_archive_data_by_date(archive_data):
	grouped_archive_data = []
	distinct_dates = {}
	sorted_dates = []
	for m in archive_data:
		if m["date"] in distinct_dates:
			distinct_dates[m["date"]] += [m]
		else:
			distinct_dates[m["date"]] = [m]
			sorted_dates += [m["date"]]

	for date in sorted_dates:
		grouped_archive_data += [distinct_dates[date]]

	return grouped_archive_data

def archive(request):
	matches_collection = mongo.init_collection('matches')
	matches = mongo.query_collection(matches_collection)

	# reverse matches so in reverse chronological order
	matches = matches[::-1]

	archive_data = []
	for m in matches:
		match_data = {}
		match_data["date"] = format_match_dt_from_db(m["date"])
		match_data["home"] = m["home"]
		match_data["away"] = m["away"]
		match_data["home_crest"] = os.path.join(
                                'club-crests',
                                m['home'].lower().replace(' ', '_') + '-crest.png')
		match_data["away_crest"] = os.path.join(
                                'club-crests',
                                m['away'].lower().replace(' ', '_') + '-crest.png')
		match_data["url"] = create_match_url(m['home'], m['away'], m['timestamp'], 'archive')
		archive_data += [match_data]

	archive_data = group_archive_data_by_date(archive_data)

	template = loader.get_template('archive.html')
	context = RequestContext(request, {
		'archive_data' : archive_data,
		})

	return HttpResponse(template.render(context))

def archive_match(request, team1, team2, timestamp):
	archive_collection = mongo.init_collection('archive')
	home = team1.title().replace('_', ' ')
	away = team2.title().replace('_', ' ')
	home_crest = os.path.join('club-crests', team1 + '-crest.png')
	away_crest = os.path.join('club-crests', team2 + '-crest.png')
	query = {"home" : home,
				"away" : away,
				"timestamp" : int(timestamp)}
	print query
	match_data = mongo.query_collection(archive_collection, query)[0]
	print match_data

	template = loader.get_template('archive_match.html')
	context = RequestContext(request, {
		'home' : home,
		'away' : away,
		'home_crest' : home_crest,
		'away_crest' : away_crest,
		'match_data' : match_data
		})
	return HttpResponse(template.render(context))


def club(request, club_nm):
	#capitalize club name
	club_nm = club_nm.replace('_', ' ').title()
	have_dates = False
	template = loader.get_template('club.html')

	#add datesform to page
	form = DatesForm(request.POST or None)

	if form.is_valid():
		start_date = request.POST["start_date"]
		end_date = request.POST["end_date"]
		dt1 = datetime.datetime.strptime(start_date, '%m/%d/%Y')
		dt2 = (
			datetime.datetime.strptime(end_date, '%m/%d/%Y') +
			datetime.timedelta(days=1))
		have_dates = True

		most_popular = Tweet.objects.filter(team=club_nm) \
			.filter(created__gte=dt1) \
			.filter(created__lt=dt2) \
			.extra(select={'popularity': 'retweets+favorites'}) \
			.order_by('-popularity')[:5]
		output_popular = [
			(tweet.text[:50] + '...', tweet.url)
			for tweet in most_popular]

		if output_popular:
			have_data = True
		else:
			have_data = False

		sentiment_tweets = Tweet.objects.filter(team=club_nm) \
			.filter(created__gte=dt1) \
			.filter(created__lt=dt2)
		sent_list = count_sentiments(sentiment_tweets, dt1, dt2)
		sent_percs = sentiment_percs(dt1, dt2, sent_list)

		context = RequestContext(request, {
			'have_dates': have_dates,
			'have_data': have_data,
			'start_date': start_date,
			'end_date': end_date,
			'club_nm': club_nm,
			'dates_form': form,
			'popular_tweets': output_popular,
			'sent_percs': sent_percs,
		})
	else:
		context = RequestContext(request, {
			'have_dates': have_dates,
			'club_nm': club_nm,
			'dates_form': form,
			})

	return HttpResponse(template.render(context))
