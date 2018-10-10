from selenium import webdriver
import re

drv = webdriver.PhantomJS()
l = drv.get("http://prod.danawa.com/info/?pcode=1795206&cate=1131401")
result = drv.find_element_by_xpath('//*[@class="big_price"]')
t = result.text
re.sub(',','',t)
print(t)
