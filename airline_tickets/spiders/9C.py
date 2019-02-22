# -*- coding: utf-8 -*-
import scrapy
from airline_tickets.models import DBSession, Segment, Option, Company, Airport
from datetime import datetime, timedelta
from airline_tickets.items import TicketItem
import json


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
        'PROXY_URL': 'http://10.42.11.226:5010/get',  # use this option to disable using proxy
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
        get_time = datetime.now()
        flts = data.get('Route')
        self.logger.debug('Flights count of %s-%s on %s is %s' % (dep_airport_id, arv_airport_id, dep_date, len(flts)))
        price_type1_dict = {'5': '会员专享座', '3': '经济座', '0': '商务经济座'}
        for flt in flts:
            if len(flt) > 1:  # when the result is connecting flights,ignore this result
                continue
            flt = flt[0]
            airplane_type = flt.get('Type')
            flt_time = flt.get('FlightsTime')
            flt_no = flt.get('No')
            dep_airport_code = flt.get('DepartureAirportCode')
            dep_airport = self.session.query(Airport).filter_by(code=dep_airport_code).first()
            dep_airport_id = dep_airport_id if dep_airport is None else dep_airport.id
            dep_time = flt.get('DepartureTimeBJ')[11:16]
            stop_over = flt.get('Stopovers')
            is_direct = True
            transfer_city = None
            if stop_over:
                is_direct = False
                transfer_city = stop_over[0].get('Arrival')
            is_shared = False
            share_company = None
            share_flt_no = None
            arv_airport_code = flt.get('ArrivalAirportCode')
            arv_airport = self.session.query(Airport).filter_by(code=arv_airport_code).first()
            arv_airport_id = arv_airport_id if arv_airport is None else arv_airport.id
            arv_time = flt.get('ArrivalTimeBJ')[11:16]
            yb_price = float(flt.get('Price')) * 100
            cabins = flt.get('AircraftCabins')
            for cabin in cabins:
                cabin_infos = cabin.get('AircraftCabinInfos')
                cabin_level = cabin.get('CabinLevel')
                for cabin_info in cabin_infos:
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
                    item['price_type1'] = price_type1_dict.get(cabin_level)
                    item['price_type2'] = cabin_info.get('Name')
                    item['price'] = int(cabin_info.get('Price'))
                    item['discount'] = item['price'] / yb_price
                    item['create_date'] = get_time.strftime('%Y%m%d%H%M%S')
                    cabin_remain = cabin_info.get('Remain')
                    yield item

    def closed(self, reason):
        self.session.close()
