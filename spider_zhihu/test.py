# coding:utf8
import re
import urllib

from anaconda_project.plugins.network_util import urlparse
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
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


import sqlite3

class DataOutputer(object):

    def sqlite_open(self, dbpath=None):
        conn_sqlite = sqlite3.connect(dbpath)
        db1 = conn_sqlite.cursor()
        return db1

    def output_sqlite(self, db1, statement):
        db1.execute(statement)

    def sqlite_close(self, db1):
        db1.close()
        return None


Outputer1 = DataOutputer()
db1 = Outputer1.sqlite_open('test.db')
Outputer1.output_sqlite(db1, 'create table test1(id INT, name text)')
Outputer1.output_sqlite(db1, 'insert into test1 values(1, \'a\')')
Outputer1.output_sqlite(db1, 'select * from test1')
Outputer1.sqlite_close(db1)




c1 = 1
while c1 < 10:
    print(c1)
    c1 += 1
    if c1 == 5:
        break


try:
    print(x)
except Exception as e:
    print(e)



user_url = 'https://www.zhihu.com/people/rou-wang-wan/following'
driver.get(user_url)
url_source = driver.page_source
source_soup = BeautifulSoup(url_source, 'html.parser')

base_url = 'https://www.zhihu.com'

current_user = re.split('/', re.sub('https://www.zhihu.com/', '', user_url))[1]
current_user_tag = re.split('/', re.sub('https://www.zhihu.com/', '', user_url))[0]

# find followers
# source_soup.find_all('h2', class_='ContentItem-title')[0].find('a', class_='UserLink-link')['href']
followers = source_soup.find_all('h2', class_='ContentItem-title')


# find the number of followings
following_count = (int(source_soup.find('a', class_="Button NumberBoard-item Button--plain",
                                        href=re.compile(".*/following"))
                       .find('div', class_='NumberBoard-value')
                       .get_text()))
follower_count = (int(source_soup.find('a', class_="Button NumberBoard-item Button--plain",
                                       href=re.compile(".*/followers"))
                      .find('div', class_='NumberBoard-value')
                      .get_text()))


source_soup.find('div', class_='NumberBoard-value').get_text()

# find the number of followers

# result_data = pd.DataFrame()

count = 1
for follower in followers:
    print(count)
    user_url = follower.find('a', attrs={'data-za-detail-view-element_name':'User'})['href']
    follower_data = {}
    follower_data['user_url'] = urlparse.urljoin(base_url, user_url)
    follower_data['user_title'] = follower.find('a', attrs={'data-za-detail-view-element_name':'User'}).get_text()
    if follower.find('a', class_='UserLink-badge'):
        follower_data['org_tag'] = follower.find('a', class_='UserLink-badge')['data-tooltip']
    else:
        follower_data['org_tag'] = None

    print(follower_data)
    # result_data = result_data.append(pd.DataFrame(follower_data, index=[0]))
    count += 1

# 2017-12-24 00:20:00
driver.set_page_load_timeout(10)
answers_url = "https://www.zhihu.com/people/rou-wang-wan/answers"
driver.get(answers_url)
# driver_action = webdriver.ActionChains(driver)
# driver_action.move_to_element('h2')
time.sleep(0.5)
driver.find_element_by_css_selector('button.ProfileHeader-expandButton.Button--plain').click()
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


answers_url_source = driver.page_source
answers_source_soup = BeautifulSoup(answers_url_source, 'html.parser')

# user profile and some other things.

gender = answers_source_soup.find('meta', itemprop="gender")['content']
voteupCount = int(answers_source_soup.find('meta', itemprop="zhihu:voteupCount")['content'])
thankedCount = int(answers_source_soup.find('meta', itemprop="zhihu:thankedCount")['content'])
follower_count = int(answers_source_soup.find('meta', itemprop="zhihu:followerCount")['content'])
answer_count = int(answers_source_soup.find('meta', itemprop="zhihu:answerCount")['content'])
articlesCount = int(answers_source_soup.find('meta', itemprop="zhihu:articlesCount")['content'])

answer_page_count = math.ceil(answer_count / 20)

answers = answers_source_soup.find_all('div', class_="ContentItem AnswerItem")
print(len(answers))
answers_data = pd.DataFrame()
retry_times = 0
if (answer_page_count > 2):
    for i in range(2, answer_page_count + 1):
        print(i)
        answer_url_1 = '?'.join((answers_url, 'page={}'.format(i)))
        driver.get(answer_url_1)
        time.sleep(0.5)
        # driver.find_element_by_css_selector('button.ProfileHeader-expandButton.Button--plain').click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        answer_source_1 = driver.page_source
        answer_source_1_soup = BeautifulSoup(answer_source_1, 'html.parser')
        answer = answer_source_1_soup.find_all('div', class_="ContentItem AnswerItem")
        print(len(answer))
        while (i < answer_page_count and len(answer) < 20) or \
                (i == answer_page_count + 1 and len(answer) < answer_count - (answer_page_count - 1) * 20):
            print('retry')
            retry_times += 1
            time.sleep(0.5 * retry_times)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            answer_source_1 = driver.page_source
            answer_source_1_soup = BeautifulSoup(answer_source_1, 'html.parser')
            answer = answer_source_1_soup.find_all('div', class_="ContentItem AnswerItem")
            if retry_times > 3:
                break

        answers.extend(answer)
        print(len(answer))
        retry_times = 0

        if i > 10:
            break

print(len(answer_source_1_soup.find_all('div', class_="ContentItem AnswerItem")))

for answer in answers:
    answer_info = json.loads(answer['data-za-module-info'])
    # answer_id = int(answer_info.get('card').get('content').get('token'))
    # answer_qid = int(answer_info.get('card').get('content').get('parent_token'))
    # upvote_num = int(answer_info.get('card').get('content').get('upvote_num'))
    # comment_num = int(answer_info.get('card').get('content').get('comment_num'))

    answer_data = pd.DataFrame(answer_info.get('card').get('content'), index = [0])[['token', 'parent_token', 'upvote_num', 'comment_num']]
    answer_data['user'] = 'rou-wang-wan' ## current_user
    answer_data['question'] = answer.find('meta', itemprop='name')['content']
    answer_data['created'] = answer.find('meta', itemprop='dateCreated')['content']
    answer_data['modified'] = answer.find('meta', itemprop='dateModified')['content']

    # print(answer_data)
    answer_status = answer.find('div', class_='AnswerItem-statusContent')

    if answer_status:
        answer_data['fold'] = 1
        answer_data['fold_reason'] = answer_status.find('div', class_='AnswerItem-statusDescription').get_text()
    else:
        answer_data['fold'] = 0
        answer_data['fold_reason'] = None

    answers_data = answers_data.append(pd.DataFrame(answer_data))


# driver.find_element_by_css_selector('button.ProfileHeader-expandButton.Button--plain').click()

user_profile = pd.DataFrame()
answers_source_soup.find('div', class_='ProfileHeader-info').get_text()


# 个人信息有的有多个值，需要研究怎么处理。可以上知乎账号设置里看看，最多有多少个值  
driver.get("https://www.zhihu.com/people/luvddd/activities")
driver.find_element_by_css_selector('button.ProfileHeader-expandButton.Button--plain').click()
luvddd_source = driver.page_source
luvddd_source_soup = BeautifulSoup(luvddd_source, "html.parser")
luvddd_source_soup.find_all('div', class_='ProfileHeader-detailItem')
luvddd_source_soup.find_all('div', class_='ProfileHeader-detailItem')[2].find_all('div', class_="ProfileHeader-field")[0].get_text()


with open('source.txt', 'w', encoding='utf-8') as f:
    f.write(answers_source_soup.prettify())

f.close()