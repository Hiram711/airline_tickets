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

    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         'airline_tickets.pipelines.SqlAlchemyPipeline': 300,
    #         'airline_tickets.pipelines.MongoPipeline': 301
    #     }
    # }

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
                airline_url = 'http://b2c.csair.com/B2C40/newTrips/static/main/page/booking/index.html?t=S&c1={0}&c2={1}&d1={2}&at=1&ct=0&it=0'.format(dep_city, arv_city, date_str)
                # # this is for Selenium
                # yield scrapy.Request(airline_url, callback=self.parse, dont_filter=True,
                #                      meta={'dep_airport_id': segment.dep_airport.id,
                #                            'arv_airport_id': segment.arv_airport.id,
                #                            'dep_date': (now + timedelta(days=i)).strftime('%Y%m%d')})

                # this is for Splash
                yield SplashRequest(airline_url, callback=self.parse, endpoint='execute',
                                    args={
                                        'lua_source': script,
                                        'wait': 7
                                    },
                                    meta={'dep_airport_id': segment.dep_airport.id,
                                          'arv_airport_id': segment.arv_airport.id,
                                          'dep_date': (now + timedelta(days=i)).strftime('%Y%m%d')})

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html5lib')
        l_flt = soup.find_all(class_='zls-flight-cell')
        get_time = datetime.now()
        re_time = re.compile(r'\d{2}:\d{2}')
        re_discount = re.compile(r'.*折')
        re_price = re.compile('[0-9.,]+')
        for flt in l_flt:
            dep_airport_id = response.request.meta.get('dep_airport_id')
            arv_airport_id = response.request.meta.get('arv_airport_id')
            dep_date = response.request.meta.get('dep_date')
            flt_no = re.findall(r'[A-Z]{2}[0-9]{4}', flt.find(class_='zls-flgno-info').text)[0]
            airplane_type = flt.find(class_='zls-flgplane').text.strip()
            dep_time = re.findall(r'[0-9]{2}[:][0-9]{2}', flt.find_all(class_='zls-flgtime-dep')[0].text.strip())[0]
            arv_time = re.findall(r'[0-9]{2}[:][0-9]{2}', flt.find_all(class_='zls-flgtime-arr')[0].text.strip())[0]
            flt_time = flt.find(class_='zls-flg-time').text.replace('h', '小时').replace('m', '分钟'). \
                replace('H', '小时').replace('M', '分钟')
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
            item['create_date'] = get_time.strftime('%Y%m%d%H%M%S')
            yield item
            # is_direct = True
            # transfer_city = None
            # if flt.select_one('.summary .info .mid .zzjtzd').get_text() == '经停':
            #     is_direct = False
            #     transfer_city = flt.select_one('.summary .info .mid .zz').get_text().strip()
            # is_shared = False
            # share_company = None
            # share_flt_no = None
            # if flt.select_one('.summary .title').find_all('span')[0].string.strip() != '东方航空':
            #     is_shared = True
            #     share_company = flt.select_one('.summary .title').find_all('span')[0].string.strip()
            #     share_flt_no = flt_no
            # price_list_meta = flt.select('.body .product-list dl')
            # for price_row in price_list_meta:
            #     item = TicketItem()
            #     item['company_id'] = self.company.id
            #     item['dep_airport_id'] = dep_airport_id
            #     item['arv_airport_id'] = arv_airport_id
            #     item['dep_date'] = dep_date
            #     item['flt_no'] = flt_no
            #     item['airplane_type'] = airplane_type
            #     item['dep_time'] = dep_time
            #     item['arv_time'] = arv_time
            #     item['flt_time'] = flt_time
            #     item['is_direct'] = is_direct
            #     item['transfer_city'] = transfer_city
            #     item['is_shared'] = is_shared
            #     item['share_company'] = share_company
            #     item['share_flt_no'] = share_flt_no
            #     item['price_type1'] = price_row.parent.attrs['data-type']
            #     item['price_type2'] = price_row.find_all('dt')[0].get_text()
            #     price_info = price_row.select_one('dd.p-p').get_text()
            #     if re_discount.match(price_info):
            #         item['discount'] = float(
            #             re_price.findall(re_discount.findall(price_info)[0].strip())[0]) / 10
            #         item['price'] = int(re.sub(r',{1}', '', re_price.findall(price_info)[1].strip()))
            #     else:
            #         item['discount'] = None
            #         item['price'] = int(re.sub(r',{1}', '', re_price.findall(price_info)[0].strip()))
            #     item['create_date'] = get_time.strftime('%Y%m%d%H%M%S')
            #     yield item

    def closed(self, reason):
        self.session.close()
