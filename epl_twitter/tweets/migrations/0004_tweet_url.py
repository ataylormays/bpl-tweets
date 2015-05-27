# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0003_tweet_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='url',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
