#!/usr/bin/python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import argparse
import json
import ordinals
import os
import sys
import time

file_loc = os.path.abspath(__file__)
resources_path = os.path.join(
	os.path.dirname(os.path.dirname(os.path.dirname(file_loc))), 'resources')
sys.path.append(resources_path)
import constants


login_url = "https://twitter.com/login"
apps_url = "https://apps.twitter.com/"
new_app_url = apps_url + "/apps/new/"
app_name = "BPLTweets"
first_app_desc = (
	"Pulls Twitter data from football teams " +
	"in the British Premier League for back-end analysis")
app_desc = "%s iteration of BPL Tweets"
app_site = "https://www.linkedin.com/profile/view?id=116028429"
password = None

def enter_text(
		driver,
		find_method,
		elt_name,
		content="",
		enter=False,
		click=False):
	if find_method == "xpath":
		elt = driver.find_element_by_css_selector(elt_name)
	elif find_method == "css":
		elt = driver.find_element_by_css_selector(elt_name)
	elif find_method == "id":
		elt = driver.find_element_by_id(elt_name)

	if content != "":
		elt.send_keys(content)
	if enter:
		elt.send_keys(Keys.RETURN)
	if click:
		elt.click()

def login_to_apps_site():
	if not password:
		raise ValueError('Password has not been set. Fix code.')

	# go to log in
	driver = webdriver.Firefox()
	driver.get(login_url)
	assert "Login on Twitter" in driver.title

	# enter username/pwd
	enter_text(
		driver, "css", "input.js-username-field", "bpltweetsxxx@gmail.com")
	enter_text(
		driver, "css", "input.js-password-field", password, enter=True)

	# wait for page to load then redirect to apps site
	time.sleep(2)
	driver.get(apps_url)

	return driver


def generate_new_app(close=True):
	driver = login_to_apps_site()

	try:
		last_app_name = driver.find_element_by_xpath(
			"//li[contains(@class, 'last')]/div/div[@class='app-details']/h2/a").text
		last_app_number = int(last_app_name[len(app_name):])
	except:
		last_app_number = 0

	next_app_ordinal = ordinals.ordinal_string(last_app_number+1).title()

	driver.get(new_app_url)
	description = (
		first_app_desc if last_app_number == 0 else app_desc % next_app_ordinal)

	# enter app name/description/site, click agree
	enter_text(driver, "id", "edit-name", app_name + str(last_app_number+1))
	enter_text(driver, "id", "edit-description", description)
	enter_text(driver, "id", "edit-url", app_site)
	enter_text(driver, "id", "edit-tos-agreement", click=True)

	# click submit
	enter_text(driver, "id", "edit-submit", click=True)

	if close:
		driver.close()

def get_last_app_number():
	driver = login_to_apps_site()

	last_app_name = driver.find_element_by_xpath(
		"//li[contains(@class, 'last')]/div/div[@class='app-details']/h2/a").text
	last_app_number = int(last_app_name[len(app_name):])

	driver.close()

	return last_app_number


def get_app_credentials(
		iteration=None,
		credentials=[],
		driver=None,
		close=True):

	# first time being run
	if iteration==None:
		iteration = get_last_app_number()-1

	# last time being run
	if iteration < 0:
		driver.close()
		return credentials

	if driver==None:
		driver = login_to_apps_site()
	else:
		driver.get(apps_url)

	print 'Iteration:', iteration

	apps = driver.find_elements_by_css_selector("div.app-details")

	time.sleep(1)
	link = apps[iteration].find_element_by_xpath(".//h2/a")
	link.click()

	keys = driver.find_element_by_link_text("manage keys and access tokens")
	keys.click()

	settings_spans = driver.find_elements_by_xpath(
		"//div[@class='app-settings']/div/span")
	consumer_key = settings_spans[1].text
	consumer_secret = settings_spans[3].text

	details_spans = driver.find_elements_by_xpath(
		"//div[@class='access']/div/span")
	# generate creds consumer key and secret if not there yet
	if len(details_spans) == 0:
		driver.find_element_by_id("edit-submit-owner-token").click()
		# wait for page to load
		time.sleep(2)
		details_spans = driver.find_elements_by_xpath(
		"//div[@class='access']/div/span")
	
	access_token = details_spans[1].text
	access_token_secret = details_spans[3].text

	secrets = {'consumer_key' : consumer_key,
				'consumer_secret' : consumer_secret,
				'access_token' : access_token,
				'access_token_secret' : access_token_secret}

	credentials += [secrets]
	credentials = get_app_credentials(iteration-1, credentials, driver)

	if close:
		driver.close()

	return credentials

def write_credentials():
	credentials = get_app_credentials()
	with open(constants.SECRETS_JSON, 'w') as secrets_file:
		json.dump(credentials, secrets_file)

def delete_last_app():
	driver = login_to_apps_site()

	last_app_exists = True
	try:
		last_app = driver.find_element_by_xpath(
			"//li[(contains(@class, 'last')]/div/div[@class='app-details']/h2/a")
	except:
		last_app_exists = False

	# go into last app, click delete button, click delete
	if last_app_exists:
		driver.find_element_by_xpath(
			"//li[@class='last']/div/div[@class='app-details']/h2/a").click()
		driver.find_element_by_link_text("Delete Application").click()
		driver.find_element_by_id("edit-submit-delete").click()

	driver.close()

	return last_app_exists

def purge():
	apps_exist = delete_last_app()
	while apps_exist:
		apps_exist = delete_last_app()

def rebuild(number_of_apps=int(constants.NUM_SECRETS)):
	purge()
	for i in xrange(number_of_apps):
		print "Sleeping...", i
		time.sleep(4 * 60)
		generate_new_app()
	get_app_credentials()

def main():
	global password
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-p",
		"--password",
		type=str,
		help="Password to use for credential generation.",
		required = True)
	parser.add_argument(
		"-x",
		"--extra",
		type=int,
		help="Number of extra credentials to generate.",
		required = False)
	parser.add_argument(
		"-f",
		"--fill",
		type=bool,
		help="Boolean - if true, will add credentials until NUM_SECRETS is reached.",
		required = False)
	parser.add_argument(
		"-r",
		"--rebuild",
		type=bool,
		help="Boolean - if true, will purge credentials and rebuild NUM_SECRETS.",
		required = False)
	parser.add_argument(
		"-w",
		"--write",
		type=bool,
		help="Boolean - if true, will write credentials to SECRETS_JSON.",
		required = False)
	
	args = parser.parse_args()
	password = args.password
	extra = args.extra
	fill = args.fill
	rebuild = args.rebuild
	write = args.write
	if extra:
		for i in xrange(extra):
			print "Iteration: ", i
			generate_new_app()
			time.sleep(4 * 60)
	if fill:
		missing = constants.NUM_SECRETS - get_last_app_number()
		print missing
		for i in xrange(missing):
			print "Iteration: ", i
			generate_new_app()
			time.sleep(4 * 60)
	if rebuild:
		rebuild()
	if write:
		write_credentials()

if __name__ == '__main__':
	main()
