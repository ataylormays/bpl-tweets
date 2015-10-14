# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0005_tweet_sentiment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tweet',
            options={'managed': True},
        ),
    ]
