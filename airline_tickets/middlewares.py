# -*- coding: utf-8 -*-


from selenium import webdriver

from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from scrapy.http import HtmlResponse

from logging import getLogger


class SeleniumMiddleware:

    def __init__(self, timeout=None, executable_path=None):

        self.logger = getLogger(__name__)

        self.timeout = timeout

        self.browser = webdriver.Chrome(executable_path=executable_path)

        self.browser.set_page_load_timeout(self.timeout)

        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):

        self.browser.close()

    def process_request(self, request, spider):

        """

        用ChromeDriver抓取页面

        :param request: Request对象

        :param spider: Spider对象

        :return: HtmlResponse

        """

        self.logger.debug('Chrome is Starting')

        try:

            self.browser.get(request.url)

            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.flight')))

            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',

                                status=200)

        except TimeoutException:

            return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):

        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   executable_path=crawler.settings.get('SELENIUM_EXECUTABLE_PATH'))
