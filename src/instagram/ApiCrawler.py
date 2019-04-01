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
		self.login()
		self.userIdOfLoggedInUser = self.getUserIdOfLoggedInUser()
		self.userIdOfHandle = self.getUserIdFromInstagramHandle(self.handle)

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
			self.logger.info("Getting followings by api for handle: "+self.handle)
			queryVariables = self.getInitialQueryVariables()
			queryUrl = self.getQueryUrl('followings', queryVariables)
			self.logger.info("queryUrl: "+queryUrl)
			self.driver.get(queryUrl)
			queryResult = json.loads(self.driver.find_element_by_xpath("//body").text)
			self.logger.info("Showing "+str(queryResult['data']['user']['edge_follow']['count'])+" followings for handle: "+self.handle)
			self.followings.extend(queryResult['data']['user']['edge_follow']['edges'])
			while queryResult['data']['user']['edge_follow']['page_info']['has_next_page']:
				queryVariables["after"] = queryResult['data']['user']['edge_follow']['page_info']['end_cursor']
				queryUrl = self.getQueryUrl('followings', queryVariables)
				self.logger.info("queryUrl: "+queryUrl)
				self.driver.get(queryUrl)
				queryResult = json.loads(self.driver.find_element_by_xpath("//body").text)
				self.followings.extend(queryResult['data']['user']['edge_follow']['edges'])
			self.logger.info("Retrieved "+str(len(self.followings))+" followings for handle: "+self.handle)
		except Exception as e:
			self.logger.exception("Problem in getting followings by crawling api for handle: "+self.handle)

	def getFollowersByApi(self):
		try:
			self.logger.info("Getting followers by api for handle: "+self.handle)
		except Exception as e:
			self.logger.exception("Problem in getting followers by api for handle: "+self.handle)

	def getInitialQueryVariables(self):
		queryVariables = {}
		queryVariables["id"] = self.userIdOfHandle
		queryVariables["include_reel"] = self.config['instagram']['api']['include_reel']
		queryVariables["fetch_mutual"] = self.config['instagram']['api']['fetch_mutual']
		queryVariables["first"] = self.config['instagram']['api']['first']
		return queryVariables

	def getQueryUrl(self, typeOfQuery, queryVariables):
		queryVariablesJson = json.dumps(queryVariables).replace(" ", "")
		queryUrl = self.config['instagram']['api']['url']
		queryUrl += "?query_hash="+self.config['instagram']['api']['query_hash'][typeOfQuery]
		queryUrl += "&variables="+queryVariablesJson
		return queryUrl