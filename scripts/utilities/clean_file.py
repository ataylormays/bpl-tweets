import argparse, sys

def main():
	parser = argparse.ArgumentParser()
	try:
		parser.add_argument("filepath")
		args = parser.parse_args()
		filepath = args.filepath
	except:
		print "Must pass filepath as argument"
		sys.exit()

	try:
		with open(filepath, 'rb+') as f:
			content = f.read()
			f.seek(0)
			f.write(content.replace(b'\r', b''))
			f.truncate()
		print "Successfully cleaned file at " + filepath
	except:
		print "Failed to clean file at " + filepath

if __name__ == '__main__':
	main()