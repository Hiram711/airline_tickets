#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

response = requests.get('http://127.0.0.1:5010/get')
proxy = response.text
print(proxy)
options = Options()
options.add_argument('--proxy-server=http://%s' % proxy)
options.add_argument("--user-agent='Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1'")

driver = webdriver.Chrome(chrome_options=options, executable_path=r'D:\chromedriver_win32\chromedriver.exe')

driver.get(
    'http://b2c.csair.com/B2C40/newTrips/static/main/page/booking/index.html?t=S&c1=SHA&c2=HAK&d1=2019-02-20&at=1&ct=0&it=0')
print(driver.page_source)
# driver.quit()
