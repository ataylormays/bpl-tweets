from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import csv
import datetime
# from .models import Tweet


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

	print "HELLO"
	template = loader.get_template('home.html')
	
	today = datetime.date.today().strftime("%Y-%m-%d")
	print today
	last_wk = datetime.datetime.strptime(today, "%Y-%m-%d")-datetime.timedelta(days=7)

	recent_tweets = Tweet.objects.filter(created__gt=last_wk).filter(created__lte=today)
	hashtags = [h for tweet in recent_tweets for h in tweet.hashtags.split(", ")]

	popular_hashtags = count_elts(hashtags, 5)

	print popular_hashtags

	context = RequestContext(request, {
		'club_names': club_names,
		'hashtags': popular_hashtags,

		})
	
	context = RequestContext(request, {
		'club_names': club_names,

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

def contact(request):
	template = loader.get_template('contact.html')
	context = RequestContext(request, {
		'club_names': club_names,

		})

	return HttpResponse(template.render(context))
