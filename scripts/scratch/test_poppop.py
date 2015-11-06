import time
import os, sys

path = os.path.abspath(os.path.join('..', 'resources'))
sys.path.append(path)
import twitteraccess, constants

if __name__ == "__main__":
	test_club_nm = "Manchester United"
	# at start of match
	twitteraccess.build_params()
	twitteraccess.update_since_id(test_club_nm)
	
	# after 1st run of match, every n minutes
	since_id = twitteraccess.get_since_id(test_club_nm)
	
	runs = 1
	while(runs < constants.NUM_COLS):
		twitteraccess.populate_popularity(club_nm=test_club_nm, since_id=since_id, iteration=runs)
		time.sleep(constants.RUN_FREQ * 60)
		runs += 1