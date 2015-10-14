import datetime
import csv
import os, sys
import time

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

def remove_zeropading(time_obj):
	return time_obj[1:] if time_obj[0] == '0' else time_obj

loop = True

while(loop):
	today = datetime.date.today().strftime("%d %B %Y") 
	now = datetime.datetime.now().strftime("%I:%M %p")

	now = remove_zeropading(now)
	today = remove_zeropading(today)

	try:
		f = open(os.path.join(constants.MATCHES_DIR, "matches.csv"), 'r')
		matches_reader = csv.reader(f, delimiter=",")
		for row in matches_reader:
			if row[0] != today:
				continue
			if row[1] != time:
				continue
			home, away = row[2], row[3]
			# start processes with home and away
			print "start processes with %s and %s" % (home, away)
		f.close()

	except:
		print "Ending process"
		loop = False
	print "Sleeping for 30 secs"
	time.sleep(30)



