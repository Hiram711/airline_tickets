# -*- coding: utf-8 -*-
import scrapy
from airline_tickets.models import DBSession, Segment, Option
from datetime import datetime, timedelta
from airline_tickets.items import TicketsItemMU
from bs4 import BeautifulSoup
import re


class MuSpider(scrapy.Spider):
    name = 'MU'
    allowed_domains = ['http://www.ceair.com/']

    def __init__(self):
        super(MuSpider, self).__init__()
        self.session = DBSession()

    def start_requests(self):
        segments = self.session.query(Segment).filter_by(is_available=True).all()
        crawler_days = self.settings.get('CRAWLER_DAYS') or self.session.query(Option).filter_by(
            name='crawler_days').first()
        now = datetime.now()
        for segment in segments:
            for i in range(0, crawler_days):
                dep_city = segment.dep_airport.code.lower()
                arv_city = segment.arv_airport.code.lower()
                date_str = (now + timedelta(days=i)).strftime('%Y%m%d')[2:]
                airline_url = 'http://www.ceair.com/booking/{0}-{1}-{2}_CNY.html'.format(dep_city, arv_city,
                                                                                         date_str)
                yield scrapy.Request(airline_url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html5lib')
        l_flt = soup.find_all('article', class_='flight')
        for flt in l_flt:
            item = TicketsItemMU()
            item['flt_no'] = re.findall(r'[A-Z]{2}[0-9]+', flt.select_one('.summary .title').get_text())[0]
            item['flt_tm'] = flt.select_one('.summary').dfn.get_text()
            item['luxury_price'] = flt.select_one('.detail .head.cols-3 .luxury').get_text()
            item['economy_price'] = flt.select_one('.detail .head.cols-3 .economy').get_text()
            item['member_price'] = flt.select_one('.detail .head.cols-3 .member').get_text()
            item['airplane_type'] = \
                flt.select_one('.body .flight-details ul.detail-info li .d-4 .popup.airplane').attrs[
                    'acfamily']
            self.logger.debug('From url %s get price item :%s' % (response.url, item))
            yield item

    def closed(self, reason):
        self.session.close()
