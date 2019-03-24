from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.common.utils import *
from src.common.WebDriver import WebDriver
import time

class Crawler:
	def __init__(self, credential, handle):
		self.credential = credential
		self.handle = handle
		self.followers = []
		self.followings = []
		self.logger = getLogger("InstagramCrawler")
		self.config = loadConfiguration('config/config.yaml')
		self.driver = WebDriver().getDriver()
		self.wait = WebDriverWait(self.driver, self.config['webdriver']['wait']['time'])

	def login(self):
		try:
			self.logger.info("Logging in to instagram with handle: "+self.credential['user'])
			self.driver.get(self.config['instagram']['loginUrl'])
			self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='username'][@type='text']")))
			self.logger.debug("Presence of username field detected.")
			userNameInput = self.driver.find_element_by_xpath("//input[@name='username'][@type='text']")
			passwordInput = self.driver.find_element_by_xpath("//input[@name='password'][@type='password']")
			userNameInput.send_keys(self.credential['user'])
			passwordInput.send_keys(self.credential['password'])
			self.driver.find_element_by_xpath("//button[@type='submit']").click()
		except Exception as e:
			self.logger.exception("Fatal! Login failed.")
			return
		finally:
			self.checkSuccessfulLogin()

	def checkSuccessfulLogin(self):
		try:
			userNameInput = self.driver.find_element_by_xpath("//input[@name='username'][@type='text']")
			self.wait.until(EC.staleness_of(userNameInput))
			self.logger.info("Login successful for handle: "+self.credential['user'])
			self.logger.debug("Page url after login: "+self.driver.current_url)
		except Exception as e:
			self.logger.exception("Login failed! Invalid username or password")

	def getFollowers(self):
		try:
			self.logger.info("Retrieving followers of handle: "+self.handle)
			self.driver.get("https://instagram.com/"+self.handle)
			self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'followers')]"))) #waiting for page to load
			self.openDialog('followers')
			self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and contains(., 'Followers')]//ul//li//div[text()]")))
			self.followers = self.getListOfUsers('Followers')
			self.closeDialog()
			self.logger.info("Retrieved "+str(len(self.followers))+" followers of handle: "+self.handle)
		except Exception as e:
			self.logger.exception("Problem in getting followers of handle: "+self.handle)

	def getFollowings(self):
		try:
			self.logger.info("Retrieving following of handle: "+self.handle)
			self.driver.get("https://instagram.com/"+self.handle)
			self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'following')]"))) #waiting for page to load
			self.openDialog('following')
			self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and contains(., 'Following')]//ul//li//div[text()]")))
			self.followings = self.getListOfUsers('Following')
			self.closeDialog()
			self.logger.info("Retrieved "+str(len(self.followings))+" followings of handle: "+self.handle)
		except Exception as e:
			self.logger.exception("Problem in getting followings of handle: "+self.handle)

	def openDialog(self, typeOfDialog):
		self.logger.debug("Opening "+typeOfDialog+" dialog of handle: "+self.handle)
		linkToOpenDialog = self.driver.find_element_by_xpath("//a[contains(@href, '{}')]".format(typeOfDialog))
		try:
			#Followers number may be like 2.5m. span['title'] contains followers like 1,122,445
			numberOfUsersInDialog = int(linkToOpenDialog.find_element_by_xpath(".//span[@title]").get_attribute("title").replace(',', ''))
		except Exception as e:
			#span['title'] is missing in following. Following count in instagram is limited to 7500.
			numberOfUsersInDialog = int(linkToOpenDialog.find_element_by_xpath(".//span").text)
		self.logger.info("Number of "+typeOfDialog+" of "+self.handle+" showing: "+str(numberOfUsersInDialog))
		linkToOpenDialog.click()
		self.logger.debug(typeOfDialog+" dialog opened of handle:"+self.handle)

	'''
	Instagram has throttling enabled. Rate varies from account to account. Generally near 200 requests per hour.
	Number of followers/following shown on profile is not always accurate. That's why we stop when we can't scroll more.
	'''
	def getListOfUsers(self, dialogType):
		dialog = self.driver.find_element_by_xpath("//div[@role='dialog' and contains(., '{}')]".format(dialogType))
		userCount = 0
		previousCount = 0
		numberOfScrollsWithoutNewUsers = 0
		while numberOfScrollsWithoutNewUsers < self.config['instagram']['scrollsWithoutNewUsersLimit']:
			self.scrollDialogAndSleepForSometime(dialog)
			userCount = len(dialog.find_elements_by_xpath(".//ul//li"))
			if userCount == previousCount:
				numberOfScrollsWithoutNewUsers += 1
			else:
				numberOfScrollsWithoutNewUsers = 0
			previousCount = userCount
		self.logger.info(str(userCount)+" "+dialogType+" scrolled by getListOfUsers()")
		userWebElements = dialog.find_elements_by_xpath(".//ul//li//a[@title]")
		users = []
		for user in userWebElements:
			users.append(user.get_attribute('title'))
		return users

	def scrollDialogAndSleepForSometime(self, dialog):
		actions = ActionChains(self.driver)
		# send PAGE_DOWN key on the last retrieved user
		actions.send_keys_to_element(dialog.find_elements_by_xpath(".//ul//li//div[text()]")[-1], Keys.PAGE_DOWN)
		actions.perform()
		time.sleep(self.config['instagram']['sleepTimeAfterScroll'])

	def closeDialog(self):
		self.logger.debug("Closing dialog")
		closeDialogButton = self.driver.find_element_by_xpath("//*[@aria-label='Close']")
		closeDialogButton.click()
		self.logger.debug("Closing dialog successful")

	def closeSession(self):
		self.driver.quit()