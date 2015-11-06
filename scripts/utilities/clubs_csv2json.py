import json
import csv
import os, sys

path = os.path.abspath(os.path.join('..', 'resources'))
sys.path.append(path)

try:
	import constants
except ImportError, e:
	print 'sys_path: ', sys.path
	constants = __import__('constants')
	print 'constants: %r' % constants
	try:
		print 'constants is at %s (%s)' % (constants.__file__, constants.__path__)
	except Exception, e:
		print 'Cannot give details on constants (%s)' % e

clubs_dict = {}
with open(os.path.join(constants.DATA_DIR, "twitter_clubs.csv"), 'r') as clubs_csv:
	clubs = csv.reader(clubs_csv, delimiter=",")
	headers = clubs.next()
	for row in clubs:
		club_nm = row[0]
		club_dict = {}
		for index, elt in enumerate(row):
			club_dict[headers[index]] = elt
		clubs_dict[club_nm] = club_dict

with open(os.path.join(constants.DATA_DIR, "twitter_clubs.json"), 'w') as clubs_json:
	json.dump(clubs_dict, clubs_json, indent=1)