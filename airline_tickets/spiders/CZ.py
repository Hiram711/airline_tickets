# -*- coding: utf-8 -*-
import scrapy
from airline_tickets.models import DBSession, Segment, Option, Company
from datetime import datetime, timedelta
from airline_tickets.items import TicketItem
from bs4 import BeautifulSoup
from scrapy_splash.request import SplashRequest

import re

# the lua script is for Splash to disable images load,visit the target website and wait for a specific time
script = """
function main(splash, args)
  splash.images_enabled = false
  splash:set_user_agent(args.user_agent)
  splash:go(args.url)
  splash:wait(args.wait)
  splash:set_viewport_full()
  splash:wait(args.wait)
  click_items=splash:select_all('.zls-cabin-cell')
  for k,v in ipairs(click_items)
  do
    click_item=v
    click_item:mouse_click()
    splash:wait(0.5)
  end
  return splash:html()
end
"""


class CzSpider(scrapy.Spider):
    name = 'CZ'

    # # this is for Selenium
    # custom_settings = {
    #     'SELENIUM_TIMEOUT': 30,
    #     'SPIDER_MIDDLEWARES': {},  # disable splash
    #     'DOWNLOADER_MIDDLEWARES':
    #         {
    #             'airline_tickets.middlewares.RandomUserAgentMiddleware': 553,
    #             'airline_tickets.middlewares.ProxyMiddleware': 554,
    #             'airline_tickets.middlewares.SeleniumMiddleware': 555,
    #         },
    #     'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',  # disable splash and using default setting
    #     'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',  # disable splash and using default setting
    #     'PROXY_URL': 'http://10.42.11.226:5010/get',  # use this option to disable using proxy
    # }

    # this is for Splash
    custom_settings = {
        # 'CONCURRENT_REQUESTS': 7,  # use this option to make the requests handled one by one
        'USE_PROXY_DEFAULT': False,
        'PROXY_URL': 'http://10.42.11.226:5010/get',  # use this option to disable using proxy
    }

    def __init__(self):
        super(CzSpider, self).__init__()
        self.session = DBSession()
        self.company = self.session.query(Company).filter_by(prefix='CZ').first()

    def start_requests(self):
        segments = self.session.query(Segment).filter_by(is_available=True).all()
        crawler_days = self.settings.get('CRAWLER_DAYS') or self.session.query(Option).filter_by(
            name='crawler_days').first()
        now = datetime.now()
        for segment in segments:
            for i in range(0, crawler_days):
                dep_city = segment.dep_airport.code.upper()
                arv_city = segment.arv_airport.code.upper()
                date_str = (now + timedelta(days=i)).strftime('%Y-%m-%d')
                airline_url = 'http://b2c.csair.com/B2C40/newTrips/static/main/page/booking/index.html?t=S&c1={0}&c2={1}&d1={2}&at=1&ct=0&it=0'.format(
                    dep_city, arv_city, date_str)
                # this is for Splash
                yield SplashRequest(airline_url, callback=self.parse, endpoint='execute',
                                    args={
                                        'lua_source': script,
                                        'wait': 10
                                    },
                                    meta={'dep_airport_id': segment.dep_airport.id,
                                          'arv_airport_id': segment.arv_airport.id,
                                          'dep_date': (now + timedelta(days=i)).strftime('%Y%m%d')})

                # # this is for Selenium
                # yield scrapy.Request(airline_url, callback=self.parse, dont_filter=True,
                #                      meta={'dep_airport_id': segment.dep_airport.id,
                #                            'arv_airport_id': segment.arv_airport.id,
                #                            'dep_date': (now + timedelta(days=i)).strftime('%Y%m%d')})

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html5lib')
        if soup.find('h3', text='验证码'):
            self.logger.error("Blocked when crawling %s" % response.url)
            return
        l_flt = soup.select('.zls-flight-cell')
        self.logger.debug('Flights count of %s-%s on %s is %s' % (
            response.request.meta.get('dep_airport_id'), response.request.meta.get('arv_airport_id'),
            response.request.meta.get('dep_date'), len(l_flt)))
        get_time = datetime.now()
        re_price = re.compile('¥[0-9.,]+')
        l_price_class1 = ['头等舱', '公务舱', '明珠经济舱', '经济舱']
        for flt in l_flt:
            if flt.find(class_='transicon tooltip-trigger'):
                continue
            dep_airport_id = response.request.meta.get('dep_airport_id')
            arv_airport_id = response.request.meta.get('arv_airport_id')
            dep_date = response.request.meta.get('dep_date')
            flt_no = re.findall(r'[A-Z]{2}[0-9]{4}', flt.find(class_='zls-flgno-info').text)[0]
            airplane_type = flt.find(class_='zls-flgplane').text.strip()
            dep_time = re.findall(r'[0-9]{2}[:][0-9]{2}', flt.find_all(class_='zls-flgtime-dep')[0].text.strip())[0]
            arv_time = re.findall(r'[0-9]{2}[:][0-9]{2}', flt.find_all(class_='zls-flgtime-arr')[0].text.strip())[0]
            flt_time = flt.find(class_='zls-flg-time').text.replace('h', '小时').replace('m', '分钟'). \
                replace('H', '小时').replace('M', '分钟')
            is_direct = True
            transfer_city = None
            mid_info = flt.select_one('.zls-trans')
            if mid_info:
                is_direct = False
                transfer_city = re.findall(r'([^：]+)$', mid_info)[0].replace(' ', '')
            is_shared = False
            share_company = None
            share_flt_no = None
            share_info = flt.find(attrs={'data-tip-class': 'share-show'})
            if share_info:
                is_shared = True
                share_company = share_info.attrs['data-share'].split('#')[0]
                share_flt_no = share_info.attrs['data-share'].split('#')[2]
            price_list_meta = flt.find_all(class_='zls-price-cell')
            for price_row in price_list_meta:
                item = TicketItem()
                item['company_id'] = self.company.id
                item['dep_airport_id'] = dep_airport_id
                item['arv_airport_id'] = arv_airport_id
                item['dep_date'] = dep_date
                item['flt_no'] = flt_no
                item['airplane_type'] = airplane_type
                item['dep_time'] = dep_time
                item['arv_time'] = arv_time
                item['flt_time'] = flt_time
                item['is_direct'] = is_direct
                item['transfer_city'] = transfer_city
                item['is_shared'] = is_shared
                item['share_company'] = share_company
                item['share_flt_no'] = share_flt_no
                item['price_type1'] = l_price_class1[int(price_row.parent.parent.attrs['data-cabin'])]
                item['price_type2'] = price_row.select_one('.cabin-info .cabin-name').get_text()
                price_info = price_row.select_one('.cabin-other').find_all('li')[1].get_text().replace('折', '')
                item['discount'] = 1.0 if price_info == '全 价' else float(price_info) / 10
                item['price'] = int(
                    re_price.findall(price_row.select_one('.cabin-price-info').get_text())[0].replace('¥', ''))
                item['create_date'] = get_time.strftime('%Y%m%d%H%M%S')
                yield item

    def closed(self, reason):
        self.session.close()
