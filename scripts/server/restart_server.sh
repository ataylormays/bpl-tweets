#!/bin/bash

# django commands
python /home/ubuntu/BplTweets/bpl-tweets/epl_twitter/manage.py collectstatic

# Restart nginx
nginx -s reload
service nginx restart

# Restart gunicorn
supervisorctl reread
supervisorctl update
supervisorctl restart epl_twitter

