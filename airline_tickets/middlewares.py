# -*- coding: utf-8 -*-

import random
import requests
from logging import getLogger

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class RandomUserAgentMiddleware:

    def __init__(self):
        self.user_agents = [

            'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',

            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',

            'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',

            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',

            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',

            'Opera/8.0 (Windows NT 5.1; U; en)',

            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',

        ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)


class ProxyMiddleware:

    def __init__(self, proxy_url):

        self.logger = getLogger(__name__)

        self.proxy_url = proxy_url

    def get_random_proxy(self):

        try:
            if self.proxy_url:
                response = requests.get(self.proxy_url)
            else:
                return False

            if response.status_code == 200:
                proxy = response.text

                return proxy

        except requests.ConnectionError:

            return False

    def process_request(self, request, spider):

        proxy = self.get_random_proxy()

        if proxy:
            uri = 'https://{proxy}'.format(proxy=proxy)

            self.logger.debug('Using proxy' + proxy)

            request.meta['proxy'] = uri

    @classmethod
    def from_crawler(cls, crawler):

        settings = crawler.settings

        return cls(

            proxy_url=settings.get('PROXY_URL')

        )


class SeleniumMiddleware:

    def __init__(self, timeout=None, executable_path=None):

        self.logger = getLogger(__name__)

        self.timeout = timeout

        self.executable_path = executable_path

    def process_request(self, request, spider):

        """

        用ChromeDriver抓取页面

        :param request: Request对象

        :param spider: Spider对象

        :return: HtmlResponse

        """

        try:
            options = Options()

            options.headless = True

            proxy = request.meta.get('proxy')

            user_agent = request.headers.get('User-Agent')

            if proxy:
                options.add_argument('--proxy-server=%s' % proxy)

            if user_agent:
                options.add_argument('--user-agent="%s"' % user_agent)

            browser = webdriver.Chrome(chrome_options=options, executable_path=self.executable_path)

            browser.set_page_load_timeout(self.timeout)

            wait = WebDriverWait(browser, self.timeout)

            self.logger.debug('Chrome is Starting')

            browser.get(request.url)

            if spider.name == 'MU':
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.flight')))

            return HtmlResponse(url=request.url, body=browser.page_source, request=request, encoding='utf-8',

                                status=200)

        except TimeoutException:

            return HtmlResponse(url=request.url, status=500, request=request)

        finally:

            browser.close()

    @classmethod
    def from_crawler(cls, crawler):

        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   executable_path=crawler.settings.get('SELENIUM_EXECUTABLE_PATH'))
