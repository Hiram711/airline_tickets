# -*- coding: utf-8 -*-
import scrapy
import json
from airline_tickets.models import DBSession, Segment, Option, Company
from datetime import datetime, timedelta
from airline_tickets.items import TicketItem


class CzSpider(scrapy.Spider):
    name = 'CZ'

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
        super(CzSpider, self).__init__()
        self.session = DBSession()
        self.company = self.session.query(Company).filter_by(prefix='CZ').first()
        self.api_url = 'http://b2c.csair.com/portal/flight/direct/query'
        self.headers = {
            'Host': 'b2c.csair.com',
            'Accept': 'application/json,text/javascript,*/*;q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.csair.com/cn/index.shtml',
            'Connection': 'keep-alive',
        }

    def start_requests(self):
        segments = self.session.query(Segment).filter_by(is_available=True).all()
        crawler_days = self.settings.get('CRAWLER_DAYS') or self.session.query(Option).filter_by(
            name='crawler_days').first()
        now = datetime.now()
        for segment in segments:
            for i in range(0, crawler_days):
                dep_city = segment.dep_airport.code.upper()
                arv_city = segment.arv_airport.code.upper()
                date_str = (now + timedelta(days=i)).strftime('%Y%m%d')
                data = {
                    'action': '0',
                    'adultNum': '1',
                    'airLine': 1,
                    'arrCity': arv_city,
                    'cabinOrder': '0',
                    'cache': 0,
                    'childNum': '0',
                    'depCity': dep_city,
                    'flightDate': date_str,
                    'flyType': 0,
                    'infantNum': '0',
                    'international': '0',
                    'isMember': '',
                    'preUrl': '',
                    'segType': '1',
                }
                yield scrapy.FormRequest(self.api_url, callback=self.parse, dont_filter=True,
                                         headers=self.headers, formdata=data,
                                         meta=
                                         {
                                             'dep_airport_id': segment.dep_airport.id,
                                             'arv_airport_id': segment.arv_airport.id,
                                             'dep_date': date_str
                                         }
                                         )

    def parse(self, response):
        data = json.loads(response.text)
        dep_airport_id = response.request.meta.get('dep_airport_id')
        arv_airport_id = response.request.meta.get('arv_airport_id')
        dep_date = response.request.meta.get('dep_date')
        if data.get('success') == 'false':
            self.logger.debug('Flights count of %s-%s on %s is 0' % (dep_airport_id, arv_airport_id, dep_date))
            return
        airplane_type_list = data.get('data').get('planes')
        l_flt = data.get('data').get('segment').get('dateFlight').get('flight')
        self.logger.debug('Flights count of %s-%s on %s is %s' % (
            response.request.meta.get('dep_airport_id'), response.request.meta.get('arv_airport_id'),
            response.request.meta.get('dep_date'), len(l_flt)))
        get_time = datetime.fromtimestamp(int(data.get('data').get('createTime')) / 1000)
        fb_price = int(data.get('data').get('segment').get('dateFlight').get('fbasic').get('adultPrice'))
        jb_price = int(data.get('data').get('segment').get('dateFlight').get('jbasic').get('adultPrice'))
        wb_price = int(data.get('data').get('segment').get('dateFlight').get('wbasic').get('adultPrice'))
        yb_price = int(data.get('data').get('segment').get('dateFlight').get('ybasic').get('adultPrice'))
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
