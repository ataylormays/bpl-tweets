# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0002_tweet_is_retweet'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='team',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
