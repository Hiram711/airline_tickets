# -*- coding: utf-8 -*-
import scrapy


class HttpBinSpider(scrapy.Spider):
    name = 'httpbin'
    start_urls = ['http://httpbin.org/get']

    def parse(self, response):
        self.logger.debug('Page info is \n %s' % response.text)
