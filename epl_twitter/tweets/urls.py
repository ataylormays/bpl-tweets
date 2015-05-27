from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.teams, name='teams'),
	url(r'^(?P<club_nm>[A-Za-z_]+)/$', views.club, name='club'),
]