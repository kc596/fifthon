from src.common.utils import *
from src.instagram.UICrawler import UICrawler

class Instagram:
	def __init__(self, credential, handle):
		self.credential = credential 	#credential used to log in
		self.handle = handle 			#handle to crawl
		self.logger = getLogger("Instagram")
		self.followers  = []
		self.followings = []
		self.crawler = UICrawler(credential, handle)
		self.crawl()
		#self.dbHandler = Database()
		#self.dataAnalyser = Analysis()
		
	def crawl(self):
		self.logger.info("Crawling instagram of handle: "+self.handle)
		self.crawler.login()
		#self.crawler.getUserIdOfLoggedInUser()
		self.crawler.getFollowersHandleByScrollingUI()
		self.crawler.getFollowingsHandleByScrollingUI()
		self.crawler.closeSession()
		self.followers = self.crawler.followers
		self.followings = self.crawler.followings
		self.logger.info("Crawling done. Retrieved: "+str(len(self.followers))+" followers and "+str(len(self.followings))+" followings")