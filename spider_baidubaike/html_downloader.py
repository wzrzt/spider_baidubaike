# coding:utf8
import urllib.request

# from selenium import webdriver


class HtmlDownloader(object):

    def download(self, url):
        if url is None:
            return None

    #    driver_dir = "/home/weirain/Apps/chromedriver/chromedriver"
    #    driver = webdriver.Chrome(driver_dir)  # 打开浏览器

    #   driver.get(url)

    #    response = driver.page_source  # 这是原网页 HTML 信息

        response = urllib.request.urlopen(url)

        if response.getcode() != 200:
            return None

        return response.read()

  #  driver_dir = "/home/weirain/Apps/chromedriver/chromedriver"
   # driver = webdriver.Chrome(driver_dir)   # 打开浏览器
   # driver.get("https://www.zhihu.com/people/meretsger/answers")

   # result_raw = driver.page_source