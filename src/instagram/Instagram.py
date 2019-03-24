from src.common.utils import *
from src.instagram.Crawler import Crawler

class Instagram:
	def __init__(self, credential, handle):
		self.credential = credential 	#credential used to log in
		self.handle = handle 			#handle to crawl
		self.logger = getLogger("Instagram")
		self.followers  = []
		self.followings = []
		self.crawler = Crawler(credential, handle)
		self.crawl()
		#self.dbHandler = Database()
		#self.dataAnalyser = Analysis()
		
	def crawl(self):
		self.logger.info("Crawling instagram of handle: "+self.handle)
		self.crawler.login()
		self.crawler.getFollowers()
		self.crawler.getFollowings()
		self.crawler.closeSession()
		self.followers = self.crawler.followers
		self.followings = self.crawler.followings
		self.logger.info("Crawling done. Retrieved: "+str(len(self.followers))+" followers and "+str(len(self.followings))+" followings")