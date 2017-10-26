# coding:utf8

# coding:utf8
import re
import urllib
import math

from anaconda_project.plugins.network_util import urlparse
from bs4 import BeautifulSoup

import os
from selenium import webdriver

import time
import random

import sqlite3
import json
import pandas as pd

root_url = "https://www.zhihu.com/people/meretsger/following"
# 打开浏览器
if os.environ['HOME'] == '/Users/weirain':
    webdriver_path = '/Users/weirain/Tools/webdrivers/chromedriver'
elif os.environ['HOME'] == '/home/weirain':
    webdriver_path = '/home/weirain/Apps/chromedriver/chromedriver'

driver = webdriver.Chrome()





def CrawUsers(user):

    base_url = 'https://www.zhihu.com'
    following_url = urlparse.urljoin(base_url, "/".join((user, 'following')))
#    current_url = urlparse.urljoin(zhihu_url, "/".join((current_user, 'following')))
    answers_url = urlparse.urljoin(zhihu_url, "/".join((current_user, 'answers')))

    # return base_user_url

    driver.get(following_url)
    url_source = driver.page_source
    source_soup = BeautifulSoup(url_source, 'html.parser')

    # find the number of followings and calculate total page numbers of followings.
    following_count = (int(source_soup.find('a', class_="Button NumberBoard-item Button--plain",
                                            href=re.compile(".*/following"))
                           .find('div', class_='NumberBoard-value')
                           .get_text()))
    following_page_count = math.ceil(following_count / 20)

    followings = source_soup.find_all('h2', class_='ContentItem-title')

    if (following_page_count > 2):
        for i in range(2, following_page_count + 1):
            user_following_url = '?'.join((following_url, 'page={}'.format(i)))
            driver.get(user_following_url)
            url_source = driver.page_source
            source_soup = BeautifulSoup(url_source, 'html.parser')
            followings.extend(source_soup.find_all('h2', class_='ContentItem-title'))


    if len(followings) == 0:
        return None
    else:
        result_data = pd.DataFrame()
        for following in followings:
            following_user = following.find('a', attrs={'data-za-detail-view-element_name': 'User'})['href']
            following_data = {}

            following_data['following_user'] = following_user
            following_data['following_user_title'] = following.find('a', attrs={'data-za-detail-view-element_name': 'User'}).get_text()
            if following.find('a', class_='UserLink-badge'):
                following_data['Certification_tag'] = following.find('a', class_='UserLink-badge')['data-tooltip']
            else:
                following_data['Certification_tag'] = None
            result_data = result_data.append(pd.DataFrame(following_data, index=[0]))

        return result_data # , following_data_all




result_data = pd.DataFrame()
# root_url = 'https://www.zhihu.com/people/meretsger'
# root_user = {'tag': 'people', 'webname': 'meretsger'}
root_user = "/people/meretsger"
zhihu_url = 'https://www.zhihu.com'
newUserSet = set()
oldUserSet = set()

newUserSet.add(root_user)


craw_count = 0

while len(newUserSet) > 0:
    print(craw_count)

    current_user = newUserSet.pop()
    # current_url = urlparse.urljoin(zhihu_url, "/".join((current_user, 'following')))
    # answers_url = urlparse.urljoin(zhihu_url, "/".join((current_user, 'answers')))

    oldUserSet.add(current_user)
    # current_user_name = re.split('/', re.sub('https://www.zhihu.com/', '', user))[1]
    try:
        result_data1 = CrawUsers(current_user)
        result_data1['current_user'] = current_user
        result_data1['id'] = craw_count
        # print(current_user_name)
        # print(result_data1)
        for following_user in result_data1['following_user']:
            if following_user not in oldUserSet:
                newUserSet.add(following_user)
        print("""Crawing {}'s followers ... ... """.format(current_user))
        print("""His/her webname is {}""".format(current_user))
        print(result_data1.shape)
        result_data = result_data.append(result_data1, ignore_index=True)

    except Exception as e:
        print(e)
        print("""User {} craw failed""".format(current_user))

    craw_count += 1
    if craw_count == 10:
        break

    # if current_user_name == 'rou-wang-wan':
    #     break


driver.close()



