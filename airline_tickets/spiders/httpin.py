# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash.request import SplashRequest

# the lua script is for Splash to disable images load,visit the target website and wait for a specific time
script = """
function main(splash, args)
  splash.images_enabled = false
  assert(splash:go(args.url))
  assert(splash:wait(args.wait))
  return splash:html()
end
"""


class HttpBinSpider(scrapy.Spider):
    name = 'httpbin'

    # start_urls = ['http://httpbin.org/get']

    def start_requests(self):
        yield SplashRequest('http://httpbin.org/get', callback=self.parse, endpoint='execute',
                            args={
                                'lua_source': script,
                                'wait': 3}
                            )

    def parse(self, response):
        self.logger.debug('Page info is \n %s' % response.text)
