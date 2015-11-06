import csv

main_dir = "C:/Users/ataylor/Documents/Projects/web apps/epl twitter"
clubs_file_nm = main_dir + "/data/twitter_clubs.csv"
with open(clubs_file_nm) as clubs_file:
	club_names = []
	clubs = csv.reader(clubs_file, delimiter=",")
	#skip header row
	next(clubs)
	for row in clubs:
		club_names.extend([(row[0].replace(' ', '_').lower(), row[0])])

print club_names

# club_names2 = [club.replace('_', ' ').title() for club in club_names]
# print club_names2
# test comment for commit
