# coding:utf8
import urllib.request

# from selenium import webdriver


class HtmlDownloader(object):

    def download(self, url, driver):
        if url is None:
            return None

        driver.get(url)

        response = driver.page_source  # 这是原网页 HTML 信息

        # response = urllib.request.urlopen(url)

        if response is None:
            return None

        return response