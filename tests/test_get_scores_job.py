import os, sys
import unittest
import time, datetime

file_loc = os.path.abspath(__file__)
resources_path = os.path.join(
	os.path.dirname(os.path.dirname(file_loc)), 'resources')
sys.path.append(resources_path)
import constants

# import other libs
import_paths = [constants.JOBS_DIR, constants.UTILITIES_DIR]
for ip in import_paths:
	print ip
	sys.path.append(ip)

import get_scores_job as scores
import mongo_utilities as mongo

class TestProcessDaemon(unittest.TestCase):

	def setUp(self):
		self.archive_collection = mongo.init_collection('archive', 'test')
		self.home = "Bournemouth"
		self.away = "Manchester United"
		self.timestamp = 1471143099

		self.archive_collection.remove({})
		
		self.test_archive = { 
							"home" : self.home,
							"away" : self.away,
							"timestamp" : self.timestamp,
							"top_tweets" : [],
							"top_hashtags" : [],
							"counts" : []
						}
		mongo.insert_object(self.archive_collection, self.test_archive)

	def tearDown(self):
		self.archive_collection.remove({})
		
	def test_get_scores_job_missing_score(self):
		scores.main('test')

		records = mongo.query_collection(self.archive_collection)
		archive_record = records[0]
		self.assertTrue("score" in archive_record)
		self.assertEquals("1-3", archive_record["score"])

	def test_get_scores_job_existing_score(self):

		# add false score to match
		update = {"score" : "1-6"}
		mongo.update_one(self.archive_collection, self.test_archive, update)

		scores.main('test')

		records = mongo.query_collection(self.archive_collection)
		archive_record = records[0]
		self.assertTrue("score" in archive_record)
		self.assertNotEqual("1-3", archive_record["score"])

if __name__ == '__main__':
	unittest.main()
