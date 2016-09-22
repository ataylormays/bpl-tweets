import os, sys
import unittest
import time, datetime

file_loc = os.path.abspath(__file__)
resources_path = os.path.join(
	os.path.dirname(os.path.dirname(file_loc)), 'resources')
sys.path.append(resources_path)
import constants

# import other libs
daemon_path = os.path.join(constants.SCRIPTS_DIR, 'process_daemon')
import_paths = [daemon_path, constants.UTILITIES_DIR]
for ip in import_paths:
	sys.path.append(ip)

import process_daemon
import mongo_utilities as mongo

class TestProcessDaemon(unittest.TestCase):

	def setUp(self):
		self.matches_collection = mongo.init_collection('matches', 'test')
		self.live_collection = mongo.init_collection('live', 'test')

		self.home = "Manchester United"
		self.away = "Manchester City"
		self.start = time.time() + 90
		dt = self.timestamp_to_human_times(self.start)
		test_match = { "timestamp" : self.start, "home" : self.home, "away" : self.away, "human_time" : dt[1], "date" : dt[0]}
		mongo.insert_object(self.matches_collection, test_match)

	def tearDown(self):
		self.matches_collection.remove({})
		self.live_collection.remove({})

	def timestamp_to_human_times(self, ts):
		date = datetime.datetime.fromtimestamp(ts).date().strftime('%d %B %Y')
		time = datetime.datetime.fromtimestamp(ts).time().strftime('%H:%M')
		return (date, time)
		
	def test_process_daemon(self):
		match_query = {'timestamp': {'$gt': 1470787379.0}}
		matches = mongo.query_collection(self.matches_collection, match_query)
		self.assertEqual(len(matches), 1)

		duration = 2 * 60
		process_daemon.dummy_mode(self.home, self.away, self.start, duration)

		match_query = {"home" : self.home, "away" : self.away, "timestamp" : self.start}
		matches = mongo.query_collection(self.matches_collection, match_query)
		self.assertEqual(len(matches), 1)
		match = matches[0]
		self.assertTrue( "live" in match )

		tweets_query = {"match_ts": {"$gt": self.start}, "unix_ts": {"$gt": self.start}}
		tweets = mongo.query_collection(self.live_collection, tweets_query)
		self.assertGreater(len(tweets), 0)

if __name__ == '__main__':
	unittest.main()
