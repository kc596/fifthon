class ApiCrawler:
	def __init__(self):
		self.userIdOfLoggedInUser = -1
		self.userIdOfHandle = -1

	def getFollowersByApi(self):
		try:
			self.logger.info("Getting followers by api for handle: "+self.handle)
		except Exception as e:
			self.logger.exception("Problem in getting followers by api for handle: "+self.handle)

	def getUserIdOfLoggedInUser(self):
		try:
			self.logger.info("Getting user id of logged in user: "+self.credential['user'])
			allCookies = self.driver.get_cookies()
			for cookie in allCookies:
				if(cookie['name']=='ds_user_id'):
					self.userIdOfLoggedInUser = cookie['value']
					break
			if self.userIdOfLoggedInUser == -1:
				raise Exception('Unable to get ds_user_id cookie. Either login failed or some problem in cookies.')
			self.logger.info("ds_user_id cookie {}: {}".format(self.credential['user'], self.userIdOfLoggedInUser))
		except Exception as e:
			self.logger.exception("Problem in getting userIdOfLoggedInUser from cookies.")

	def getUserIdFromInstagramHandle(self, handle):
		print('nothing')