from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^(?P<team1>[A-Za-z_]+)-(?P<team2>[A-Za-z_]+)-(?P<date>[0-9]{4}[0-1][0-9][0-3][0-9])/$', views.demo, name='home'),
]
