# coding:utf8

import re
import math
from anaconda_project.plugins.network_util import urlparse
from bs4 import BeautifulSoup
import os
from selenium import webdriver
import time
import sqlite3
import json
import pandas as pd


def craw_following(user, driver):

    base_url = 'https://www.zhihu.com'
    following_url = urlparse.urljoin(base_url, "/".join((user, 'following')))

    driver.get(following_url)
    time.sleep(0.5)

    url_source = driver.page_source
    source_soup = BeautifulSoup(url_source, 'html.parser')

    # find the number of followings and calculate total page numbers of followings.
    following_count = (int(source_soup.find('a', class_="Button NumberBoard-item Button--plain",
                                            href=re.compile(".*/following"))
                           .find('div', class_='NumberBoard-value')
                           .get_text()))
    print("following_count: {}".format(following_count))

    if following_count == 0:
        return None
    else:
        following_page_count = math.ceil(following_count / 20)
        followings = source_soup.find_all('h2', class_='ContentItem-title')

        retry_times = 0
        if following_page_count > 2:
            for i in range(2, int(following_page_count) + 1):
                user_following_url = '?'.join((following_url, 'page={}'.format(i)))
                driver.get(user_following_url)
                time.sleep(0.5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                url_source = driver.page_source
                source_soup = BeautifulSoup(url_source, 'html.parser')
                following_more = source_soup.find_all('h2', class_='ContentItem-title')
                while (i < following_page_count and len(following_more) < 20) or \
                        (i == following_page_count and len(following_more) < following_count -
                            (following_page_count - 1) * 20):

                    retry_times += 1
                    time.sleep(0.5 * retry_times)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    url_source = driver.page_source
                    source_soup = BeautifulSoup(url_source, 'html.parser')
                    following_more = source_soup.find_all('h2', class_='ContentItem-title')

                followings.extend(following_more)
                retry_times = 0

        followings_data = pd.DataFrame()
        for following in followings:

            following_user = following.find('a', attrs={'data-za-detail-view-element_name': 'User'})['href']
            following_data = {}

            following_data['following_user'] = following_user
            following_data['following_user_title'] = following.find('a', attrs={'data-za-detail-view-element_name': 'User'}).get_text()
            if following.find('a', class_='UserLink-badge'):
                following_data['Certification_tag'] = following.find('a', class_='UserLink-badge')['data-tooltip']
            else:
                following_data['Certification_tag'] = None

            followings_data = followings_data.append(pd.DataFrame(following_data, index=[0]))
        followings_data['current_user'] = user

        return followings_data


def craw_user_info(user, driver):

    """craw user information"""

    base_url = 'https://www.zhihu.com'
    following_url = urlparse.urljoin(base_url, "/".join((user, 'following')))
    driver.get(following_url)
    url_source = driver.page_source
    source_soup = BeautifulSoup(url_source, 'html.parser')

    privacy = source_soup.find_all('div', class_="ProfileMainPrivacy-mainContentWrapper")
    user_name = source_soup.find('span', class_="ProfileHeader-name").get_text()

    if not privacy:

        # find the number of followings and calculate total page numbers of followings.
        following_count = (int(source_soup.find('a', class_="Button NumberBoard-item Button--plain",
                                                href=re.compile(".*/following"))
                               .find('div', class_='NumberBoard-value')
                               .get_text()))

        time.sleep(0.5)
        try:
            driver.find_element_by_css_selector('button.ProfileHeader-expandButton.Button--plain').click()
        except Exception as no_bottom:
            pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        answers_url_source = driver.page_source
        answers_source_soup = BeautifulSoup(answers_url_source, 'html.parser')

        # user profile and some other things.

        # 个人信息有的有多个值，需要研究怎么处理。可以上知乎账号设置里看看，最多有多少个值

        user_profile = {}
        user_infos = answers_source_soup.find_all('div', class_='ProfileHeader-detailItem')

        if user_infos:
            for user_info in user_infos:
                # print("key:{};value:{}".format(user_info.find('span', class_='ProfileHeader-detailLabel').get_text(),
                #                                user_info.find('div', class_='ProfileHeader-detailValue').get_text()))
                keyname = user_info.find('span', class_='ProfileHeader-detailLabel').get_text()
                keyvalue = user_info.find('div', class_='ProfileHeader-detailValue')
                keyvalue_sub = keyvalue.find_all('div', class_='ProfileHeader-field')
                if keyvalue_sub:
                    for i in range(len(keyvalue)):
                        user_profile[keyname] = ";".join(map(lambda x: x.get_text(), keyvalue_sub))
                else:
                    user_profile[keyname] = keyvalue.get_text()

            # user_profile = pd.DataFrame(user_profile, index=[0])
            user_profile = pd.DataFrame([user_profile],
                columns=['个人简介', '居住地', '所在行业', '职业经历', '教育经历'])
            user_profile.rename(columns={'个人简介': 'self_introduce',
                                         '居住地': 'living_area',
                                         '所在行业': 'industry',
                                         '职业经历': 'work_experience',
                                         '教育经历': 'education'}, inplace=True)
        else:
            user_profile = pd.DataFrame()

        user_headline1 = answers_source_soup.find('span', class_="RichText ProfileHeader-headline")
        if user_headline1:
            user_headline = user_headline1.get_text()
        else:
            user_headline = None

        gender = answers_source_soup.find('meta', itemprop="gender")['content']
        voteup_count = int(answers_source_soup.find('meta', itemprop="zhihu:voteupCount")['content'])
        thanked_count = int(answers_source_soup.find('meta', itemprop="zhihu:thankedCount")['content'])
        follower_count = int(answers_source_soup.find('meta', itemprop="zhihu:followerCount")['content'])
        answer_count = int(answers_source_soup.find('meta', itemprop="zhihu:answerCount")['content'])
        articles_count = int(answers_source_soup.find('meta', itemprop="zhihu:articlesCount")['content'])

        user_profile['web_name'] = user
        user_profile['privacy'] = 0
        user_profile['user_name'] = user_name
        user_profile['headline'] = user_headline
        user_profile['gender'] = gender
        user_profile['voteup_count'] = voteup_count
        user_profile['thanked_count'] = thanked_count
        user_profile['following_count'] = following_count
        user_profile['follower_count'] = follower_count
        user_profile['articles_count'] = articles_count
        user_profile['answer_count'] = answer_count
        print("user:{}; user_name:{}".format(user, user_name, user_headline))

    else:
        user_profile = pd.DataFrame({'web_name': user, 'privacy': 1, 'user_name': user_name})

    return user_profile


def craw_answers(user, driver):

    """craw a user's anwsers."""

    base_url = 'https://www.zhihu.com'
    answers_url = urlparse.urljoin(base_url, "/".join((user, 'answers')))
    driver.get(answers_url)

    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    answers_url_source = driver.page_source
    answers_source_soup = BeautifulSoup(answers_url_source, 'html.parser')

    answer_count = int(answers_source_soup.find('meta', itemprop="zhihu:answerCount")['content'])
    print("answer_count: {}".format(answer_count))

    if answer_count == 0:
        return None
    else:
        answer_page_count = math.ceil(answer_count / 20)

        answers = answers_source_soup.find_all('div', class_="ContentItem AnswerItem")
        # print(len(answers))
        answers_data = pd.DataFrame()
        retry_times = 0
        if answer_page_count > 2:
            for i in range(2, int(answer_page_count) + 1):
                # print(i)
                answer_url_1 = '?'.join((answers_url, 'page={}'.format(i)))
                driver.get(answer_url_1)
                time.sleep(0.5)
                # driver.find_element_by_css_selector('button.ProfileHeader-expandButton.Button--plain').click()
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                answer_source_1 = driver.page_source
                answer_source_1_soup = BeautifulSoup(answer_source_1, 'html.parser')
                answer = answer_source_1_soup.find_all('div', class_="ContentItem AnswerItem")
            # print(len(answer))
                while (i < answer_page_count and len(answer) < 20) or \
                        (i == answer_page_count and len(answer) < answer_count - (answer_page_count - 1) * 20):
                    # print('retry')
                    retry_times += 1
                    time.sleep(0.5 * retry_times)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    answer_source_1 = driver.page_source
                    answer_source_1_soup = BeautifulSoup(answer_source_1, 'html.parser')
                    answer = answer_source_1_soup.find_all('div', class_="ContentItem AnswerItem")
                    if retry_times > 3:
                        break

                answers.extend(answer)
            #    print(len(answer))
                retry_times = 0

        for answer in answers:
            answer_info = json.loads(answer['data-za-module-info'])

            answer_data = pd.DataFrame(answer_info.get('card').get('content'), index=[0])[
                ['token', 'parent_token', 'upvote_num', 'comment_num']]
            answer_data['user'] = 'rou-wang-wan'  # current_user
            answer_data['question'] = answer.find('meta', itemprop='name')['content']
            answer_data['created'] = answer.find('meta', itemprop='dateCreated')['content']
            answer_data['modified'] = answer.find('meta', itemprop='dateModified')['content']

            answer_status = answer.find('div', class_='AnswerItem-statusContent')

            if answer_status:
                answer_data['fold'] = 1
                fold_reason = answer_status.find('div', class_='AnswerItem-statusDescription')
                if fold_reason:
                    answer_data['fold_reason'] = fold_reason.get_text()
                else:
                    answer_data['fold_reason'] = None
            else:
                answer_data['fold'] = 0
                answer_data['fold_reason'] = None

            answers_data = answers_data.append(pd.DataFrame(answer_data))

        return answers_data


def main(max_craw):

    print("start !")

    # root_url = "https://www.zhihu.com/people/meretsger/following"
    # 打开浏览器
    if os.environ['HOME'] == '/Users/weirain':
        webdriver_path = '/Users/weirain/Tools/webdrivers/chromedriver'
    elif os.environ['HOME'] == '/home/weirain':
        webdriver_path = '/home/weirain/Apps/chromedriver/chromedriver'

    driver = webdriver.Chrome(webdriver_path)

    # 数据库

    sqlite_db_connect = sqlite3.Connection("zhihu_data.db")
    sqlite_db = sqlite_db_connect.cursor()

    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", sqlite_db_connect)

    # followings_df = pd.DataFrame()
    # user_df = pd.DataFrame()
    # answers_df = pd.DataFrame()
    # root_url = 'https://www.zhihu.com/people/meretsger'
    # root_user = {'tag': 'people', 'webname': 'meretsger'}

    newUserSet = set()
    if 'users' in tables['name']:
        oldUserlist = pd.read_sql("select id, web_name from users", sqlite_db_connect)
        oldUserSet = set(oldUserlist['web_name'])
        if len(oldUserSet) > 0:
            craw_count = max(oldUserlist['id'])
            root_user = oldUserlist['web_name'][-1]
    else:
        oldUserSet = set()
        craw_count = 0
        root_user = "/people/meretsger"

    newUserSet.add(root_user)

    while len(newUserSet) > 0:
        print("Crawing No.{} user...".format(craw_count))
        current_user = newUserSet.pop()
        oldUserSet.add(current_user)
        print("""His/her webname is {}""".format(current_user))

        user_profile = pd.DataFrame()
        try:
            user_profile = craw_user_info(current_user, driver=driver)
            user_profile['id'] = craw_count
            user_profile.to_sql("users", con=sqlite_db_connect, if_exists='append', index=False)

        except Exception as user_info_e:
            print(user_info_e)
            print("""User information of {} craw failed""".format(current_user))

        if (not user_profile.empty) and user_profile['privacy'][0] != 1:

            try:
                followings_data = craw_following(current_user, driver=driver)
                # print(current_user_name)
                # print(result_data1)
                for following_user in followings_data['following_user']:
                    if following_user not in oldUserSet:
                        newUserSet.add(following_user)

                print("followings data shape", followings_data.shape, sep=':')
                followings_data.to_sql("followings", con=sqlite_db_connect, if_exists='append', index=False)

            except Exception as following_e:
                print(following_e)
                print("""following of {} craw failed or he/she has no following""".format(current_user))

            try:
                answers_data = craw_answers(current_user, driver=driver)
                print("answers data shape", answers_data.shape, sep=':')
                answers_data.to_sql('answers', sqlite_db_connect, if_exists='append', index=False)

            except Exception as answer_e:
                print(answer_e)
                print("""following of {} craw failed or he/she has no answer""".format(current_user))

            craw_count += 1
            if craw_count == max_craw:
                break

    driver.close()
    sqlite_db.close()


if __name__ == '__main__':
    main(max_craw=1000)
