from src.common.utils import *
from Analyser import Analyser
from Crawler import Crawler

class Instagram:
    def __init__(self, credential, handle):
        self.credential = crendential   #credential used to log in
        self.handle = bdHandler         #handle to crawl
        self.logger = getLogger("Instagram")
        
        #self.crawler = Crawler(driver, crendential, handle)
        #self.bdHandler = Database()
        #self.dataAnalyser = Analysis()
        
    def printData(self):
        self.logger.error("Instagram class")
        return