# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0004_tweet_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='sentiment',
            field=models.CharField(default='neutral', max_length=10),
            preserve_default=False,
        ),
    ]
