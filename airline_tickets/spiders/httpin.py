# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash.request import SplashRequest

# the lua script is for Splash to disable images load,visit the target website and wait for a specific time
script = """
function main(splash, args)
  splash.images_enabled = false
  splash:set_user_agent(args.user_agent)
 -- This script is no more useful and replaced by the middleware ProxyMiddleware 
 -- splash:on_request(
 --   function(request)
 --   request:set_proxy{
 --       host = "118.190.95.34",
 --       port = 9001,
 --       type = 'http'
 --   }
 --   end)
  splash:go(args.url)
  splash:wait(args.wait)
  return splash:html()
end
"""


class HttpBinSpider(scrapy.Spider):
    name = 'httpbin'

    # # this is for selenium
    # start_urls = ['http://httpbin.org/get']

    custom_settings = {
        'USE_PROXY_DEFAULT': True,
        'PROXY_URL': 'http://10.42.11.226:5010/get',
    }

    # this is for splash
    def start_requests(self):
        yield SplashRequest('http://httpbin.org/get', callback=self.parse, endpoint='execute',
                            args={
                                'lua_source': script,
                                'wait': 3}
                            )

    def parse(self, response):
        self.logger.debug('Page info is \n %s' % response.text)
