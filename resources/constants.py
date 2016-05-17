

import os
import logging

# 90 min game + 15 min half time + 15 min buffer = 120 min
TOT_MINUTES = 120
RUN_FREQ = 1

# number of cols in popularity file
NUM_COLS = TOT_MINUTES / RUN_FREQ

# number of secrets
NUM_SECRETS = 15

# refresh time for getting new keys for Twitter API call
REFRESH_TIME = 45 * 60

# result type for twitter queries (popular, recent, mixed)
TWEET_TYPE = "popular"

# Twitter API endpoint
RESOURCE_URL = "https://api.twitter.com/1.1/search/tweets.json"

# phrases to remove from query results
BANNED_PHRASES = [
	"RT",
	"PRE ORDER",
	"PRE-ORDER"
]

# live vs. placeholder
LIVE_MODE = True

# mongo collections to use
QA_MODE = not LIVE_MODE

# directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRESTS_DIR = os.path.join(BASE_DIR, 'epl_twitter/assets/images/club-crests/')
RESOURCES_DIR = os.path.join(BASE_DIR, "resources/")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "bpl-tweets-data/")
SECRETS_DIR = os.path.join(DATA_DIR, "secrets/")
MATCHES_DIR = os.path.join(DATA_DIR, "matches/")
LOGS_DIR = os.path.join(DATA_DIR, "logs/")
PARAMS_DIR = os.path.join(SECRETS_DIR, "params/")
CONSUMERS_DIR = os.path.join(SECRETS_DIR, "consumers/")
TOKENS_DIR = os.path.join(SECRETS_DIR, "tokens/")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts/")
UTILITIES_DIR = os.path.join(SCRIPTS_DIR, "utilities/")

# logging
LOG_LEVEL = logging.DEBUG
LOG_FILE = os.path.join(LOGS_DIR, "bpl-tweets.log")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# files
SECRETS_CSV = os.path.join(SECRETS_DIR, "secrets.csv")
SECRETS_JSON = os.path.join(SECRETS_DIR, "secrets.json")
CLUBS_CSV = os.path.join(RESOURCES_DIR, "twitter_clubs.csv")
CLUBS_JSON = os.path.join(RESOURCES_DIR, "twitter_clubs.json")

# db configs
TWITTER_TIME_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'
TWITTER_DB = {'prod':'twitter_db','qa':'twitter_test_db'}
TWITTER_COLLECTIONS = {'prod':{}, 'qa':{}}
TWITTER_COLLECTIONS["prod"]["tweets"] = 'twitter_collection'
TWITTER_COLLECTIONS["prod"]["live"] = 'live_tweets'
TWITTER_COLLECTIONS["prod"]["popular"] = 'popular_tweets'
TWITTER_COLLECTIONS["prod"]["matches"] = 'matches'
TWITTER_COLLECTIONS["prod"]["archive"] = 'archive'
TWITTER_COLLECTIONS["qa"]["tweets"] = 'twitter_test_collection'
TWITTER_COLLECTIONS["qa"]["live"] = 'live_test_tweets'
TWITTER_COLLECTIONS["qa"]["popular"] = 'popular_test_tweets'
TWITTER_COLLECTIONS["qa"]["matches"] = 'test_matches'
TWITTER_COLLECTIONS["qa"]["archive"] = 'test_archive'

#Archive configs
ARCHIVE_START = "August 2015"