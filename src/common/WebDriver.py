from src.common.utils import *
from selenium import webdriver

class WebDriver:
	def __init__(self):
		self.logger = getLogger("WebDriver")
		self.driver = None
		try:
			self.driver = webdriver.Chrome('drivers/chromedriver')
			self.logger.info("Initialized selenium webdriver.")
		except Exception as e:
			self.logger.error("Unable to get selenium webdriver!")

	def getDriver(self):
		return self.getChromeDriver()

	def getChromeDriver(self):
		return self.driver
