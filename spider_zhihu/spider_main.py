# coding:utf8
import os
import sqlite3
import urllib

from selenium import webdriver

from spider_baidubaike import url_manager, html_downloader, html_parser, html_outputer
import time
import random

from spider_zhihu import DataOutputer


class SpiderMain(object):
    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()
        self.outosql = DataOutputer.DataOutputer()

    def craw(self, root_url, driver):
        count = 1
        self.urls.add_new_url(root_url)

        while self.urls.has_new_url():
            try:
                new_url = self.urls.get_new_url()

                # urllib.parse.unquote 让 url 的中汉语部分显示出来

                print("crawing %d : %s" % (count, urllib.parse.unquote(new_url)))
                html_cont = self.downloader.download(new_url, driver)
                new_urls, new_data = self.parser.parse(new_url, html_cont)
                self.urls.add_new_urls(new_urls)
                self.outputer.collect_data(new_data)

                if count == 1000:
                    break

                count += 1
                #        time.sleep(1)

            except:
                print("craw failed")

        self.outputer.output_html()


if __name__ == "__main__":
    root_url = "https://baike.baidu.com/item/Python/407313"
    # 打开浏览器
    if os.environ['HOME'] == '/Users/weirain':
        webdriver_path = '/Users/weirain/Tools/webdrivers/chromedriver'
    elif os.environ['HOME'] == '/home/weirain':
        webdriver_path = '/home/weirain/Apps/chromedriver/chromedriver'

    driver = webdriver.Chrome()
    db = sqlite3.connect()
    obj_spider = SpiderMain()
    obj_spider.craw(root_url, driver)
    driver.close() 