from selenium import webdriver
from getpass import getpass  
import time
from getpass import getpass 
 
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
driver = webdriver.Chrome(chrome_options=options)

driver.get('https://instagram.com/')
time.sleep(3)

driver.find_element_by_link_text("Log in").click()
time.sleep(3)

usr=raw_input('Enter Email Id:')  
#pwd=raw_input('Enter Password:')
pwd = getpass('Enter Password:')

username_box = driver.find_element_by_name("username") 
username_box.send_keys(usr)

password_box = driver.find_element_by_name("password") 
password_box.send_keys(pwd)

login_box = driver.find_element_by_css_selector("button[class='_0mzm- sqdOP  L3NKy       '][type='submit']") 
login_box.click() 

#driver.quit()