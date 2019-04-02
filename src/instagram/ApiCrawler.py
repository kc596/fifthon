from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.common.utils import *
from src.common.WebDriver import WebDriver
from src.instagram.UILogin import UILogin
import json
import re
import time

class ApiCrawler:
	def __init__(self, credential, handle):
		self.credential = credential
		self.handle = handle
		self.loggedIn = False
		self.followers = []
		self.followings = []
		self.logger = getLogger("InstagramApiCrawler")
		self.config = loadConfiguration('config/config.yaml')
		self.driver = WebDriver().getDriver()
		self.wait = WebDriverWait(self.driver, self.config['webdriver']['wait']['time'])
		self.apiRequestCount = 0
		self.login()
		self.userIdOfLoggedInUser = self.getUserIdOfLoggedInUser()
		self.userIdOfHandle = self.getUserIdFromInstagramHandle(self.handle)
		#self.getFollowingsByApi()
		#self.getFollowersByApi()
		#self.closeSession()

	def login(self):
		try:
			self.loggedIn = UILogin(self.driver, self.credential).login()
			if self.loggedIn==False:
				raise Exception("Unsuccessful login.")
		except Exception as e:
			self.logger.exception("Login failed! Handle: "+self.credential['user'])

	def getUserIdOfLoggedInUser(self):
		try:
			self.logger.info("Getting user id of logged in user: "+self.credential['user'])
			idOfTargetHandle = 0
			assert self.loggedIn, "First login to instagram before getting userid"
			self.driver.get(self.config['instagram']['handleBaseUrl']+self.credential['user'])	# provides time for cookie to load
			allCookies = self.driver.get_cookies()
			for cookie in allCookies:
				if(cookie['name']=='ds_user_id'):
					idOfTargetHandle = cookie['value']
					break
			if idOfTargetHandle == 0:
				raise Exception('Unable to get ds_user_id cookie. Either login failed or some problem in cookies.')
			self.logger.info("ds_user_id cookie {}: {}".format(self.credential['user'], idOfTargetHandle))
			return idOfTargetHandle
		except Exception as e:
			self.logger.exception("Problem in getting userIdOfLoggedInUser from cookies for handle:"+self.credential['user'])
			return 0

	def getUserIdFromInstagramHandle(self, handle):
		try:
			self.logger.info("Getting user id of handle: "+handle)
			self.driver.get("view-source:"+self.config['instagram']['handleBaseUrl']+handle+"/")
			searchResult = re.search(self.config['instagram']['regexToGetIdFromHtmlSource'], self.driver.find_element_by_xpath("//body").text)
			# print(re.split(",", searchResult.group())) -> "has_requested_viewer":false,"id":"178537482","is_business_account":t
			self.logger.debug("Found regex in html source: "+str(re.split(",", searchResult.group())))
			idOfTargetHandle = 0
			for keyValue in re.split(",", searchResult.group()):
				if "id" in keyValue:
					idOfTargetHandle = keyValue[6:-1]
			if idOfTargetHandle == 0:
				raise Exception("Unable to obtain id of target handle: {} from html source".format(handle))
			self.logger.info("id of handle {} from html source: {}".format(handle, idOfTargetHandle))
			return idOfTargetHandle
		except Exception as e:
			self.logger.exception("Problem in getUserIdFromInstagramHandle(using html source):"+self.handle)
			return 0

	def getFollowingsByApi(self):
		try:
			self.followings = self.getUsersByApi('followings', 'edge_follow')
		except Exception as e:
			self.logger.exception("Problem in getting followings by crawling api for handle: "+self.handle)

	def getFollowersByApi(self):
		try:
			self.followers = self.getUsersByApi('followers', 'edge_followed_by')
		except Exception as e:
			self.logger.exception("Problem in getting followers by api for handle: "+self.handle)

	def getUsersByApi(self, typeOfUsers, typeOfEdge):
		users = []
		self.logger.info("Getting "+typeOfUsers+" by api for handle: "+self.handle)
		queryVariables = self.getInitialQueryVariables()
		queryUrl = self.getQueryUrl(typeOfUsers, queryVariables)
		self.logger.info("First queryUrl: "+queryUrl)
		self.makeApiCall(queryUrl)
		queryResult = json.loads(self.driver.find_element_by_xpath("//body").text)
		self.logger.info("Showing "+str(queryResult['data']['user'][typeOfEdge]['count'])+" "+typeOfUsers+" for handle: "+self.handle)
		users.extend(queryResult['data']['user'][typeOfEdge]['edges'])
		while queryResult['data']['user'][typeOfEdge]['page_info']['has_next_page']:
			queryVariables["after"] = queryResult['data']['user'][typeOfEdge]['page_info']['end_cursor']
			queryUrl = self.getQueryUrl(typeOfUsers, queryVariables)
			self.logger.info("Retrieving next set of "+typeOfUsers+" for handle: "+self.handle)
			self.logger.debug("Query variables: "+str(json.dumps(queryVariables).replace(" ", "")))
			self.makeApiCall(queryUrl)
			queryResult = json.loads(self.driver.find_element_by_xpath("//body").text)
			users.extend(queryResult['data']['user'][typeOfEdge]['edges'])
		self.logger.info("Retrieved "+str(len(users))+" "+typeOfUsers+" for handle: "+self.handle)
		return users

	def getInitialQueryVariables(self):
		queryVariables = {}
		queryVariables["id"] = self.userIdOfHandle
		queryVariables["include_reel"] = self.config['instagram']['api']['include_reel']
		queryVariables["fetch_mutual"] = self.config['instagram']['api']['fetch_mutual']
		queryVariables["first"] = self.config['instagram']['api']['first']
		return queryVariables

	def getQueryUrl(self, typeOfUsers, queryVariables):
		queryVariablesJson = json.dumps(queryVariables).replace(" ", "")
		queryUrl = self.config['instagram']['api']['url']
		queryUrl += "?query_hash="+self.config['instagram']['api']['query_hash'][typeOfUsers]
		queryUrl += "&variables="+queryVariablesJson
		return queryUrl

	def makeApiCall(self, url):
		self.driver.get(url)
		self.apiRequestCount += 1
		if self.apiRequestCount >= self.config['instagram']['api']['limit']:
			time.sleep(3600)
			self.apiRequestCount = 0
		else:
			time.sleep(self.config['instagram']['api']['sleepTimeAfterQuery'])

	def closeSession(self):
		self.driver.quit()