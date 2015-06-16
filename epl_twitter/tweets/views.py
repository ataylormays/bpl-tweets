from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import Tweet
import csv
from forms import DatesForm
import datetime
import time
import os

#create club_names variable
#list of tuples, eg ("manchester_united", "Manchester United")
MAIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
clubs_file_nm = os.path.join(MAIN_DIR, "data/twitter_clubs.csv")

with open(clubs_file_nm) as clubs_file:
	club_names = []
	clubs = csv.reader(clubs_file, delimiter=",")
	#skip header row
	next(clubs)
	for row in clubs:
		club_names.extend([(row[0].replace(' ', '_').lower(), row[0])])

def extract_date(dt):
	# 2015-05-17 12:11:00 -> 2015-05-17
	return dt[:10]

def count_elts(numbers, limit):
	output = {}
	for n in numbers:
		if n in output.keys():
			output[n] += 1
		else:
			output[n] = 1
	return sorted(output.items(), key=lambda x:-1*x[1])[:limit]

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
	return L

def count_sentiments(tweets, dt1, dt2):
	sents = create_sent_list(dt1, dt2)
	dates = create_date_dict(dt1, dt2)
	for t in tweets:
		formatted_dt = t.created.strftime("%Y-%m-%d")
		if t.sentiment == 'positive':
			sents[dates[formatted_dt]][1][0] += 1
		elif t.sentiment == 'neutral':
			sents[dates[formatted_dt]][1][1] += 1
		else:
			sents[dates[formatted_dt]][1][2] += 1
	return sents

# compute percentages of each sentiment
# returns dict with d[date] = [% pos, % neut, % neg]
def sentiment_to_perc(sent_dict):
	d = {}
	for date in sent_dict.keys():
		sent_total = float(sum(sent_dict[date]))
		print date, sent_total
		if sent_total == 0:
			d[date] = [0, 0, 0]
		else:
			d[date] = [round(100*sent_dict[date][0]/sent_total, 2),
						round(100*sent_dict[date][1]/sent_total, 2),
						round(100*sent_dict[date][2]/sent_total, 2)]
	return sorted(d.items(), key=lambda x:-1*x[1])

def home(request):

	template = loader.get_template('home.html')
	
	today = datetime.date.today().strftime("%Y-%m-%d")
	last_wk = datetime.datetime.strptime(today, "%Y-%m-%d")-datetime.timedelta(days=7)

	recent_tweets = Tweet.objects.filter(created__gt=last_wk).filter(created__lte=today)
	hashtags = [h for tweet in recent_tweets for h in tweet.hashtags.split(", ")]

	# remove occurences of empty strings

	hashtags = [h for h in hashtags if h != ""]

	popular_hashtags = [(count, elt[0], elt[1]) for count, elt in enumerate(count_elts(hashtags, 20), 1)]
	
	context = RequestContext(request, {
		'club_names': club_names,
		'hashtags': popular_hashtags,

		})

	return HttpResponse(template.render(context))

def about(request):
	today = datetime.date.today().strftime("%b %d, %Y")
	template = loader.get_template('about.html')
	context = RequestContext(request, {
		'club_names': club_names,
		'today': today,

		})

	return HttpResponse(template.render(context))

def teams(request):
	template = loader.get_template('teams.html')
	context = RequestContext(request, {
		'club_names': club_names,
		})
	return HttpResponse(template.render(context))

def contact(request):
	template = loader.get_template('contact.html')
	context = RequestContext(request, {
		'club_names': club_names,

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
		print start_date
		end_date = request.POST["end_date"]
		dt1 = datetime.datetime.strptime(start_date, '%m/%d/%Y')
		print dt1
		dt2 = datetime.datetime.strptime(end_date, '%m/%d/%Y')+datetime.timedelta(days=1)
		have_dates = True
		most_popular = Tweet.objects.filter(team=club_nm).filter(created__gte=dt1).filter(created__lt=dt2).extra(select={'popularity': 'retweets+favorites'}).order_by('-popularity')[:5]
		output_popular = [(tweet.text[:50] + '...', tweet.url) for tweet in most_popular]
		if output_popular:
			have_data = True
		else:
			have_data = False

		sentiment_tweets = Tweet.objects.filter(team=club_nm).filter(created__gte=dt1).filter(created__lt=dt2)
		sentiment_dict = count_sentiments(sentiment_tweets, dt1, dt2)
		perc_sent = sentiment_to_perc(sentiment_dict)

		context = RequestContext(request, {
			'have_dates': have_dates,
			'have_data': have_data,
			'start_date': start_date,
			'end_date': end_date,
			'club_nm': club_nm,
			'club_names': club_names,
			'dates_form': form,
			'popular_tweets': output_popular,
			'perc_sent': perc_sent,
		})
	else:
		context = RequestContext(request, {
			'have_dates': have_dates,
			'club_nm': club_nm,
			'club_names': club_names,
			'dates_form': form,
			})

	return HttpResponse(template.render(context))
