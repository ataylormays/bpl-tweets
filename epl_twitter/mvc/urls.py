from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url
from . import views
from . import webservice_views
import constants

team1_regex = '(?P<team1>[A-Za-z_]+)'
team2_regex = '(?P<team2>[A-Za-z_]+)'
date_regex = '(?P<date>[0-9]{4}[0-1][0-9][0-3][0-9])'

live_regex =  team1_regex + \
	'-' + team2_regex + \
	'-' + date_regex

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

live_urlpatterns = [
	url(
                r'^tweets/ws/startAndEnd$',
                webservice_views.start_and_end,
                name='webservice'),
	url(
                r'^tweets/ws/liveTweetsCount$',
                webservice_views.live_tweets_count,
                name='liveTweetsCount'),
	url(r'^about/', views.about, name='about'),
	url(r'^archive/', views.archive, name='archive'),
	url(r'^live/' + live_regex, views.live, name='live'),
	url(r'^matches/', views.matches, name='matches'),
	url(r'^$', views.matches, name='matches')
]

placeholder_urlpatterns = [
	url(r'^', views.placeholder, name='placeholder')
]

if constants.LIVE_MODE:
	urlpatterns += live_urlpatterns
else:
	urlpatterns += placeholder_urlpatterns
