# -*- coding: utf-8 -*-
import scrapy
from airline_tickets.models import DBSession, Segment, Option, Company, Airport
from datetime import datetime, timedelta
from airline_tickets.items import TicketItem
import json
import re


class CQSpider(scrapy.Spider):
    name = '9C'

    custom_settings = {
        'SPIDER_MIDDLEWARES': {},  # disable splash
        'DOWNLOADER_MIDDLEWARES':
            {
                'airline_tickets.middlewares.RandomUserAgentMiddleware': 553,
                'airline_tickets.middlewares.ProxyMiddleware': 554,
            },
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',  # disable splash and using default setting
        'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',
        # disable splash and using default setting
        'PROXY_URL': None,  # use this option to disable using proxy
    }

    def __init__(self):
        super(CQSpider, self).__init__()
        self.session = DBSession()
        self.company = self.session.query(Company).filter_by(prefix='9C').first()

    def start_requests(self):
        api_url = 'https://flights.ch.com/Flights/SearchByTime'
        headers = {
            'Host': 'flights.ch.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache', }
        segments = self.session.query(Segment).filter_by(is_available=True).all()
        crawler_days = self.settings.get('CRAWLER_DAYS') or self.session.query(Option).filter_by(
            name='crawler_days').first()
        now = datetime.now()
        for segment in segments:
            for i in range(0, crawler_days):
                dep_city = segment.dep_airport.city
                arv_city = segment.arv_airport.city
                date_str = (now + timedelta(days=i)).strftime('%Y-%m-%d')
                data = {
                    'IsShowTaxprice': 'false',
                    'Active9s': '',
                    'IsJC': 'false',
                    'Currency': '0',
                    'SType': '0',
                    'Departure': dep_city,
                    'Arrival': arv_city,
                    'DepartureDate': date_str,
                    'ReturnDate': 'null',
                    'IsIJFlight': 'false',
                    'IsBg': 'false',
                    'IsEmployee': 'false',
                    'IsLittleGroupFlight': 'false',
                    'SeatsNum': '1',
                    'ActId': '0',
                    'IfRet': 'false',
                    'IsUM': 'false',
                    'CabinActId': 'null',
                    'isdisplayold': 'false',
                }
                yield scrapy.FormRequest(api_url, callback=self.parse, headers=headers, formdata=data,
                                         meta={'dep_airport_id': segment.dep_airport.id,
                                               'arv_airport_id': segment.arv_airport.id,
                                               'dep_date': (now + timedelta(days=i)).strftime('%Y%m%d')})

    def parse(self, response):
        data = json.loads(response.text)
        dep_date = response.request.meta.get('dep_date')
        dep_airport_id = response.request.meta.get('dep_airport_id')
        arv_airport_id = response.request.meta.get('arv_airport_id')
        flts = data.get('Route')
        self.logger.debug(data)
        for flt in flts:
            if len(flt) > 1:  # when the result is connecting flights,ignore this result
                continue
            flt = flt[0]
            airplane_type = flt.get('Type')
            flt_time = flt.get('FlightsTime')
            flt_no = flt.get('No')
            dep_date = response.request.meta.get('dep_date')
            dep_airport_code = flt.get('DepartureAirportCode')
            dep_airport = self.session.query(Airport).filter_by(code=dep_airport_code).first()
            dep_airport_id = response.request.meta.get('dep_airport_id') if dep_airport is None else dep_airport.id
            dep_time = flt.get('DepartureTimeBJ')[11:16]
            arv_airport_code = flt.get('ArrivalAirportCode')
            arv_airport = self.session.query(Airport).filter_by(code=arv_airport_code).first()
            arv_airport_id = response.request.meta.get('arv_airport_id') if arv_airport is None else dep_airport.id
            arv_time = flt.get('ArrivalTimeBJ')[11:16]
            yb_price = flt.get('Price') * 100
            cabins = flt.get('AircraftCabins')
            for cabin in cabins:
                cabin_infos = cabin.get('AircraftCabinInfos')
                cabin_level = cabin.get('CabinLevel')
                for cabin_info in cabin_infos:
                    cabin_class = cabin_info.get('Name')
                    cabin_price = cabin_info.get('Price')
                    cabin_remain = cabin_info.get('Remain')
                    print(flt_no, dep_date, dep_airport_code, arv_airport_code, flt_time, airplane_type, cabin_level,
                          cabin_class, cabin_price)

    def closed(self, reason):
        self.session.close()
