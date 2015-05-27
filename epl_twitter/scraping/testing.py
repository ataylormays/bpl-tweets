import csv
import time

main_dir = "C:/Users/ataylor/Documents/Projects/web apps/epl twitter"

clubs_file_nm = main_dir + "/data/twitter_clubs.csv"

api_params = [{
	"oath_version": number,
	"oauth_timestamp": letter,
	"lang": "en"
} for number, letter in zip([1, 3, 5], ['a', 'b', 'c'])]

x = 1 if True else 2

print x


def update_since_id_file(club_nm, since_id):
	club_file_nm = main_dir + "/data/" + club_nm.lower().replace(" ", "_") + "_since_id.txt"
	old_id = ""
	with open(club_file_nm, 'r+') as f:
		old_id = f.read()
		f.seek(0)
		f.truncate()
		f.write(since_id)
	return old_id

	# row_num = 0
	# club_row = []
	# clubs_list = []
	# with open(clubs_file_nm, 'rb') as clubs_file:
	# 	clubs = csv.reader(clubs_file, delimiter=",")
	# 	for row in clubs:
	# 		if(row[0]) == club_nm:
	# 			row[5] = since_id
	# 			club_row = [row]
	# 			break
	# 		row_num += 1

	# override = {row_num:club_row}
	# print override

	# with open(clubs_file_nm, 'rb') as clubs_file:
	# 	clubs = csv.reader(clubs_file, delimiter=",")
	# 	clubs_list.extend(clubs)
	# 	#print clubs_list


	# with open(clubs_file_nm, 'a') as clubs_file:	
	# 	writer = csv.writer(clubs_file)
	# 	for line, row in enumerate(clubs_list):
	# 		print line, row
	# 		data = override.get(line, row)
	# 		print data
	# 		writer.writerow(data)



