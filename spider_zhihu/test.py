# coding:utf8
import re
import urllib

from anaconda_project.plugins.network_util import urlparse
from bs4 import BeautifulSoup

import os
from selenium import webdriver

import time
import random

import pandas as pd

root_url = "https://www.zhihu.com/people/meretsger/following"
# 打开浏览器
if os.environ['HOME'] == '/Users/weirain':
    webdriver_path = '/Users/weirain/Tools/webdrivers/chromedriver'
elif os.environ['HOME'] == '/home/weirain':
    webdriver_path = '/home/weirain/Apps/chromedriver/chromedriver'

driver = webdriver.Chrome()
driver.get(root_url)
url_source = driver.page_source

source_soup = BeautifulSoup(url_source, 'html.parser')

base_url = 'https://www.zhihu.com'
source_soup.find_all('h2', class_='ContentItem-title')[0].find('a', class_='UserLink-link')['href']
followers = source_soup.find_all('h2', class_='ContentItem-title')

count = 1
for follower in followers:
    print(count)
    user_url = follower.find('a', attrs={'data-za-detail-view-element_name':'User'})['href']
    print(user_url)
    print(follower.find('a', attrs={'data-za-detail-view-element_name':'User'}).get_text())
    print(urlparse.urljoin(base_url, user_url))
    if follower.find('a', class_='UserLink-badge'):
        print(follower.find('a', class_='UserLink-badge')['data-tooltip'])
    count += 1


result_data = pd.DataFrame()

count = 1
for follower in followers:
    print(count)
    user_url = follower.find('a', attrs={'data-za-detail-view-element_name':'User'})['href']
    follower_data = {}
    follower_data['user_url'] = urlparse.urljoin(base_url, user_url)
    follower_data['user_title'] = follower.find('a', attrs={'data-za-detail-view-element_name':'User'}).get_text()
    if follower.find('a', class_='UserLink-badge'):
        follower_data['org_tag'] = follower.find('a', class_='UserLink-badge')['data-tooltip']
    result_data = result_data.append(pd.DataFrame(follower_data, index=[0]))
    count += 1


