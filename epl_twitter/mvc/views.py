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

def count_elts(numbers, limit):
	output = {}
	for n in numbers:
		if n in output.keys():
			output[n] += 1
		else:
			output[n] = 1
	return sorted(output.items(), key=lambda x:-1*x[1])[:limit]

def create_match_url(team1, team2, parent_dir):
	t1, t2 = (
		team1.lower().replace(' ', '_'),
		team2.lower().replace(' ', '_'))
	url = os.path.join(
		'..',
		parent_dir,
		t1 + '-' + t2 + '-' + datetime.date.today().strftime("%Y%m%d"))
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

def home(request):

	template = loader.get_template('home.html')

	today = datetime.date.today().strftime("%Y-%m-%d")
	last_wk = (
		datetime.datetime.strptime(today, "%Y-%m-%d")
		- datetime.timedelta(days=7))

	recent_tweets = Tweet.objects.filter(created__gt=last_wk) \
		.filter(created__lte=today)
	hashtags = [
		h for tweet in recent_tweets
		for h in tweet.hashtags.split(", ") if h != ""]

	popular_hashtags = [
		(count, elt[0], elt[1])
		for count, elt in enumerate(count_elts(hashtags, 20), 1)]

	context = RequestContext(request, {
		'hashtags': popular_hashtags
		})

	return HttpResponse(template.render(context))

def about(request):
	today = datetime.date.today().strftime("%b %d, %Y")
	template = loader.get_template('about.html')
	context = RequestContext(request, {
		'today': today,
		})

	return HttpResponse(template.render(context))

def matches(request):
	today = datetime.date.today().strftime("%d %B %Y")
	now = datetime.datetime.now().strftime("%I:%M %p")
	live_matches = []
	upcoming_matches = []
	try:
		csv_file = os.path.join(constants.MATCHIES_DIR, 'matches.csv')
		with open(cv_file, 'r') as f:
			matches_reader = csv.reader(f, delimiter=",")
			for row in matches_reader:
				start_dt = row[0] + " " + row[1]
				start_dt = datetime.datetime \
					.strptime(start_dt, "%d %B %Y %I:%M %p")
				delta = datetime.timedetla(
					minutes=constants.TOT_MINUTES)
				now = datetime.datetime.now()
				match = create_match_url(row[2], row[3], 'live')
				if (
					now < start_dt or
					now > start_dt + delta):
					upcoming_matches += [row + [match]]
				else:
					live_matches += [row + [match]]
	except:
		print "We fucked up in views.matches"

	template = loader.get_template('matches.html')
	context = RequestContext(request, {
		'live_matches': live_matches,
		'upcoming_matches': upcoming_matches,
		})
	return HttpResponse(template.render(context))

def live(request, team1, team2, date):
	template = loader.get_template('live.html')
	context = RequestContext(request, {
		'team1Title': team1.title().replace('_', ' '),
		'team2Title': team2.title().replace('_', ' '),
		'team1': team1,
		'team2': team2,
		'date': date,
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

def archive(request):
	date_format = "%B %Y"
	date_list = [constants.ARCHIVE_START]
	d = datetime.datetime.strptime(constants.ARCHIVE_START, date_format) \
		.date()
	end_string = (datetime.date.today() + relativedelta(months=1)) \
		.strftime(date_format)
	while(d.strftime(date_format) != end_string):
		d += relativedelta(months=1)
		date_list += [d.strftime(date_format)]

	template = loader.get_template('archive.html')
	context = RequestContext(request, {
		'date_list': date_list[::-1],
		})
	return HttpResponse(template.render(context))

def archive_match(request, team1, team2, date):
	template = loader.get_template('archive_match.html')
	context = RequestContext(request, {
		'team1': team1.title().replace('_', ' '),
		'team2': team2.title().replace('_', ' '),
		'date': date,
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
