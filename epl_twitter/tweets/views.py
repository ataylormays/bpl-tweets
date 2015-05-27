from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import Tweet
import csv
from forms import DatesForm
import datetime
import time

main_dir = "C:/Users/ataylor/Documents/Projects/web apps/epl twitter"
clubs_file_nm = main_dir + "/data/twitter_clubs.csv"
with open(clubs_file_nm) as clubs_file:
	club_names = []
	clubs = csv.reader(clubs_file, delimiter=",")
	#skip header row
	next(clubs)
	for row in clubs:
		club_names.extend([(row[0].replace(' ', '_').lower(), row[0])])

def count_elts(numbers, limit):
	output = {}
	for n in numbers:
		if n in output.keys():
			output[n] += 1
		else:
			output[n] = 1
	return sorted(output.items(), key=lambda x:-1*x[1])[:limit]

def home(request):

	template = loader.get_template('home.html')
	
	today = datetime.date.today().strftime("%Y-%m-%d")
	last_wk = datetime.datetime.strptime(today, "%Y-%m-%d")-datetime.timedelta(days=7)

	recent_tweets = Tweet.objects.filter(created__gt=last_wk).filter(created__lte=today)
	hashtags = [h for tweet in recent_tweets for h in tweet.hashtags.split(", ")]

	# remove occurences of empty strings

	hashtags = [h for h in hashtags if h != ""]

	popular_hashtags = [(count, elt[0], elt[1]) for count, elt in enumerate(count_elts(hashtags, 5), 1)]
	
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
		end_date = request.POST["end_date"]
		dt1 = datetime.datetime.strptime(start_date, '%m/%d/%Y')
		dt2 = datetime.datetime.strptime(end_date, '%m/%d/%Y')+datetime.timedelta(days=1)
		have_dates = True
		most_popular = Tweet.objects.filter(team=club_nm).filter(created__gte=dt1).filter(created__lt=dt2).extra(select={'popularity': 'retweets+favorites'}).order_by('-popularity')[:5]
		output_popular = [(tweet.text[:50] + '...', tweet.url) for tweet in most_popular]
		if output_popular:
			have_data = True
		else:
			have_data = False
		context = RequestContext(request, {
			'have_dates': have_dates,
			'have_data': have_data,
			'start_date': start_date,
			'end_date': end_date,
			'club_nm': club_nm,
			'club_names': club_names,
			'dates_form': form,
			'popular_tweets': output_popular,
		})
	else:
		context = RequestContext(request, {
			'have_dates': have_dates,
			'club_nm': club_nm,
			'club_names': club_names,
			'dates_form': form,
			})

	return HttpResponse(template.render(context))
