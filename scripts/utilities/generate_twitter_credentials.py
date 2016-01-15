from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import ordinals

login_url = "https://twitter.com/login"
apps_url = "https://apps.twitter.com/"
new_app_url = apps_url + "/apps/new/"
app_name = "BPL_Tweets"
app_desc = "%s iteration of BPL Tweets"
app_site = "https://www.linkedin.com/profile/view?id=116028429"

def enter_text(driver, find_method, elt_name, content="", enter=False, click=False):
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

	# go to log in
	driver = webdriver.Firefox()
	driver.get(login_url)
	assert "Login on Twitter" in driver.title

	# enter username/pwd
	enter_text(driver, "css", "input.js-username-field", "ataylormays@gmail.com")
	enter_text(driver, "css", "input.js-password-field", "", enter=True)

	# wait for page to load then redirect to apps site
	time.sleep(2)
	driver.get(apps_url)

	return driver


def generate_new_app(close=True):

	driver = login_to_apps_site()

	last_app_name = driver.find_element_by_xpath("//li[@class='last']/div/div[@class='app-details']/h2/a").text
	last_app_number = int(last_app_name[len(app_name):])
	next_app_ordinal = ordinals.ordinal_string(last_app_number+1).title()

	driver.get(new_app_url)

	# enter app name/description/site, click agree
	enter_text(driver, "id", "edit-name", app_name + str(last_app_number+1))
	enter_text(driver, "id", "edit-description", app_desc % next_app_ordinal)
	enter_text(driver, "id", "edit-url", app_site)
	enter_text(driver, "id", "edit-tos-agreement", click=True)

	# click submit
	enter_text(driver, "id", "edit-submit", click=True)

	if close:
		driver.close()

generate_new_app(close=False)