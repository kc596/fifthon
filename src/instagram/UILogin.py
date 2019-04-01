from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.common.utils import *

class UILogin:
	def __init__(self, driver, credential):
		self.driver = driver
		self.credential = credential
		self.logger = getLogger("InstagramUILogin")
		self.config = loadConfiguration('config/config.yaml')
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
			return self.checkSuccessfulLogin()

	def checkSuccessfulLogin(self):
		try:
			userNameInput = self.driver.find_element_by_xpath("//input[@name='username'][@type='text']")
			self.wait.until(EC.staleness_of(userNameInput))
			self.logger.info("Login successful for handle: "+self.credential['user'])
			self.logger.debug("Page url after login: "+self.driver.current_url)
			return True
		except Exception as e:
			self.logger.exception("Login failed! Invalid username or password for handle: "+self.credential['user'])
			return False