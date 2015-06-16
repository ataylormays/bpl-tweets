import urllib
import urllib2
import json
import time
from django.conf import settings
import os

# last run: 6/13/15, 11:17 AM
LAST_FINISH = 3129
LIMIT = 1000
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epl_twitter.settings")
settings.configure(
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3',
	        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	    }
	},

    )

import django
from tweets.models import Tweet

APPLICATION_ID = "153f80e3"
APPLICATION_KEY = "6a42b8f2c379f7642e4a8f0dcacb753e"

def analyze_text(text):
	parameters = {"text": text}
  	url = 'https://api.aylien.com/api/v1/sentiment'
  	headers = {
	    "Accept":                             "application/json",
	    "Content-type":                       "application/x-www-form-urlencoded",
	    "X-AYLIEN-TextAPI-Application-ID":    APPLICATION_ID,
	    "X-AYLIEN-TextAPI-Application-Key":   APPLICATION_KEY
  	}
  	opener = urllib2.build_opener()
	request = urllib2.Request(url, urllib.urlencode(parameters), headers)
	response = opener.open(request);
	return json.loads(response.read())

tweets = Tweet.objects.all()[LAST_FINISH:LIMIT+LAST_FINISH]
index = LAST_FINISH
num_hits = 0

start = time.time()
for t in tweets:
	#only allowed 60 API hits / minute
	#sleep if greater
	if(time.time() - start > 59 or num_hits > 59):
		print "Sleeping....."
		time.sleep(60)
		start = time.time()
		num_hits = 0

	#convert unicode crap	
	if u"\u2019" in t.text:
		t.text = t.text.replace(u"\u2019", '\'')
	if u"\u2014" in t.text or u"\u2013" in t.text:
		t.text = t.text.replace(u"\u2014", '-').replace(u"\u2013", '-')
	if u"\u201c" in t.text or u"\u201d" in t.text:
		t.text = t.text.replace(u"\u201c", '"').replace(u"\u201d", '"')
	if u"\u200b" in t.text:
		t.text = t.text.replace(u"\u200b", '')
	if u"\u2026" in t.text:
		t.text = t.text.replace(u"\u2026", '...')

	# hit api on tweets and analyze text
	sentiment = analyze_text(t.text.encode("utf-8"))
	t.sentiment = sentiment['polarity']
	t.save()
 	print t.team, t.sentiment, index
 	index += 1
 	num_hits += 1

