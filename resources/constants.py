import os

# 90 min game + 15 min half time + 15 min buffer = 120 min
TOT_MINUTES = 120
RUN_FREQ = .5

# number of cols in popularity file
NUM_COLS = TOT_MINUTES / RUN_FREQ

# refresh time for getting new keys for Twitter API call
REFRESH_TIME = 45 * 60

# Twitter API endpoint
RESOURCE_URL = "https://api.twitter.com/1.1/search/tweets.json"

# phrases to remove from query results
BANNED_PHRASES=[
	"RT",
	"PRE ORDER",
	"PRE-ORDER"
]

# directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data/")
SECRETS_DIR = os.path.join(DATA_DIR, "secrets/")
SINCE_DIR = os.path.join(DATA_DIR, "since_ids/")
POPULARITY_DIR = os.path.join(DATA_DIR, "popularity/")
MATCHES_DIR = os.path.join(DATA_DIR, "matches/")

# files
PARAMS_FILE = os.path.join(SECRETS_DIR, "params.json")
CONSUMERS_FILE = os.path.join(SECRETS_DIR, "consumers.con")
TOKENS_FILE = os.path.join(SECRETS_DIR, "tokens.tok")
SECRETS_FILE = os.path.join(SECRETS_DIR, "secrets.csv")
CLUBS_FILE = os.path.join(DATA_DIR, "twitter_clubs.csv")


	
