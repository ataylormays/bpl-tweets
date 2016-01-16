#!/bin/bash

NAME="epl_twitter"
DJANGODIR=/home/ubuntu/BplTweets/bpl-tweets/epl_twitter/
SOCKFILE=/home/ubuntu/BplTweets/sockets/epl_twitter-gunicorn.sock
USER=ubuntu
NUM_WORKERS=1
DJANGO_SETTINGS_MODULE=epl_twitter.settings
DJANGO_WSGI_MODULE=epl_twitter.wsgi

# Activate the virtual environment
cd $DJANGODIR
source `which virtualenvwrapper.sh`
workon $NAME
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-
