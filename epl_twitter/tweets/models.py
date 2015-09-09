from django.db import models

class Tweet(models.Model):
	
	class Meta:
		managed = True

	created = models.DateTimeField()
	team = models.CharField(max_length=30)
	favorites = models.IntegerField(default=0)
	tweet_id = models.CharField(max_length=100)
	retweets = models.IntegerField(default=0)
	text = models.CharField(max_length=420)
	url = models.CharField(max_length=100)
	hashtags = models.CharField(max_length=100)
	is_retweet = models.BooleanField(default=False)
	sentiment = models.CharField(max_length=10)

	def __unicode__(self):
		return self.text

