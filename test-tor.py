from selenium import webdriver 
from bs4 import BeautifulSoup
import time


class TorDB:
    def __init__(self):
        self._file = "test-tor-data.txt"

    def read(self):
        with open(self._file, 'r') as fileread:
            pass

service_args = [ '--proxy=localhost:9050', '--proxy-type=socks5']

driver = webdriver.PhantomJS(service_args = service_args)
#driver.get("http://www.naver.com")
driver.set_window_size(1024,768)
driver.get("http://scanlover.com")
page = driver.page_source


#element = driver.find_element_by_link_text("Censored Video Torrents")
#element.click()
#driver.find_element_by_link_text("December 2015 HD Releases Thread").click()

#with open('scanlover.txt', 'w') as outfile:
#    outfile.write(page)
username = driver.find_element_by_id("navbar_username")
password = driver.find_element_by_id("navbar_password")

username.send_keys("utylee")
password.send_keys("scanloverqnwk")

login_attempt = driver.find_element_by_xpath("//*[@type='submit']") 
login_attempt.submit()

time.sleep(8)

element = driver.find_element_by_link_text("Censored Video Torrents")
element.click()
#driver.find_element_by_link_text("December 2015 HD Releases Thread").click()

with open('scanlover.txt', 'w') as outfile:
    outfile.write(driver.page_source)

#print(element.text)

time.sleep(1)
driver.close()
