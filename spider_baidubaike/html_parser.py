# coding:utf8
import re
# import urllib
import urllib

from anaconda_project.plugins.network_util import urlparse
from bs4 import BeautifulSoup


class HtmlParser(object):

    def _get_new_urls(self, page_url, soup):
        new_urls = set()

        # <a target="_blank" href="/item/%E8%87%AA%E7%94%B1%E8%BD%AF%E4%BB%B6">自由软件</a>
        links = soup.find_all('a', href=re.compile(r'/item/[0-9a-zA-Z%]+'))
        for link in links:
            new_url = link['href']
            # new_url_tail = link.get_text()
            # new_full_url = urlparse.urljoin(page_url,  '/'.join(('/item', urllib.parse.quote(new_url_tail))))
            new_full_url = urlparse.urljoin(page_url, new_url)
            new_urls.add(new_full_url)

        return new_urls

    def _get_new_data(self, page_url, soup):

        res_data={}

        # urllib.parse.unquote 让url中的汉字显示出来
        res_data['url'] = urllib.parse.unquote(page_url)

        # <dd class="lemmaWgt-lemmaTitle-title"> <h1>Python</h1>

        title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title")

        # 先找到 h1 再获取其中的文字
        res_data['title'] = title_node.find('h1').get_text()

        # <div class="lemma-summary" label-module="lemmaSummary">
        # <div class="para" label-module="para">Python<sup>[1]</sup>
        # <a class="sup-anchor" name="ref_[1]_21087">&nbsp;
        # </a>（英国发音：/ˈpaɪθən/ 美国发音：/ˈpaɪθɑːn/）, 是一种面向对象的解释型<a target="_blank"

        summary_node = soup.find('div', class_="lemma-summary")
        res_data['summary'] = summary_node.get_text()

        return res_data

    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return

        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data

