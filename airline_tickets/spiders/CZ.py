# -*- coding: utf-8 -*-
import scrapy
import json
from airline_tickets.models import DBSession, Segment, Option, Company
from datetime import datetime, timedelta
from airline_tickets.items import TicketItem


def get_price_type1(name):
    '''
    :param name:cabin.name
    :return:
    '''
    cabin_type = {
        'F': 0,
        'J': 1,
        'C': 1,
        'D': 1,
        'I': 1,
        'O': 1,
        'W': 2,
        'S': 2,
        'gp': ['F', 'J', 'W', 'Y', 'P']
    }
    price_type = {
        0: '头等舱',
        1: '公务舱',
        2: '明珠经济舱',
        3: '经济舱',
    }
    type1 = cabin_type.get(name)
    if type1:
        return price_type.get(type1)
    else:
        return price_type.get(3)


def get_price_type2(name, cabin, basis, MemberSign='XXSL'):
    '''
    :param name: cabin.brandType[0]
    :param cabin: cabin.name,if null should be ""
    :param basis: cabin.adultFareBasis,if null should be ""
    :param MemberSign:MemberSign
    :return:
    '''
    cabin = cabin.upper()
    basis = basis.upper()
    fllang = \
        {
            'fl0188': '全价',
            'fl0080': '明珠头等舱',
            'fl0008': '头等舱',
            'fl0129': '会员专属',
            'fl0009': '公务舱',
            'fl0015': '折扣公务舱',
            'fl0010': '明珠经济舱',
            'fl0016': '折扣明珠经济舱',
            'fl0119': '全价经济舱',
            'fl0011': '经济舱',
            'fl0017': '商易旅',
            'fl0018': '优闲派',
            'fl0019': '快乐飞',
        }
    if name == 'A':
        if cabin == 'F':
            return fllang.get('fl0188') + fllang.get('fl0008')
        else:
            return fllang.get('fl0080')
    elif basis == MemberSign:
        return fllang.get('fl0129')
    elif name == 'F':
        if cabin == 'F':
            return fllang.get('fl0188') + fllang.get('fl0008')
        else:
            return fllang.get('fl0008')
    elif name == 'J':
        if cabin == 'J':
            return fllang.get('fl0188') + fllang.get('fl0009')
        else:
            return fllang.get('fl0015')
    elif name == 'W':
        if cabin == 'W':
            return fllang.get('fl0188') + fllang.get('fl0010')
        elif cabin == 'S':
            return fllang.get('fl0016')
        else:
            return fllang.get('fl0010')
    elif name == 'SW':
        if cabin == 'Y':
            return fllang.get('fl0119')
        elif cabin == 'YY':
            return fllang.get('fl0119')
        else:
            return fllang.get('fl0017')
    elif name == 'LX':
        return fllang.get('fl0018')
    elif name == 'BX':
        return fllang.get('fl0019')
    else:
        return fllang.get('fl0011')


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
        'USE_PROXY_DEFAULT': True,
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
                    'airLine': '1',  #
                    'arrCity': arv_city,
                    'cabinOrder': '0',
                    'cache': '0',  #
                    'childNum': '0',
                    'depCity': dep_city,
                    'flightDate': date_str,
                    'flyType': '0',  #
                    'infantNum': '0',
                    'international': '0',
                    'isMember': '',
                    'preUrl': '',
                    'segType': '1',
                }
                yield scrapy.FormRequest(self.api_url, callback=self.parse, dont_filter=True,
                                         headers=self.headers, body=json.dumps(data),
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
        if not data.get('success'):
            self.logger.debug('When crawling %s-%s on %s got some errors' % (dep_airport_id, arv_airport_id, dep_date))
            return None
        airplane_type_list = data.get('data').get('planes')
        l_flt = data.get('data').get('segment')[0].get('dateFlight').get('flight')
        self.logger.debug('Flights count of %s-%s on %s is %s' % (
            response.request.meta.get('dep_airport_id'), response.request.meta.get('arv_airport_id'),
            response.request.meta.get('dep_date'), len(l_flt)))

        # decrypt the json data
        for flight in l_flt:
            cabins = flight['cabin']
            cabin_group = []
            for cabin in cabins:
                cabin_group.append(
                    dict(
                        cabin=cabin['name'],
                        brand_type=cabin['brandType'][0],
                        price_type1=get_price_type1(cabin['name']),
                        price_type2=get_price_type2(cabin['brandType'][0], cabin['name'], cabin['adultFareBasis']),
                        price=cabin['adultPrice']
                    )
                )
            class_set = set()
            for i in cabin_group:
                class_set.add((i.get('price_type1'), i.get('price_type2')))
            cabin_group_show = []
            for i in class_set:
                cabin = None
                brand_type = None
                price = 9999999
                for j in cabin_group:
                    if i[0] == j.get('price_type1') and i[1] == j.get('price_type2') and int(j.get('price')) < price:
                        cabin = j.get('cabin')
                        brand_type = j.get('brand_type')
                        price = j.get('price')
                    else:
                        continue
                cabin_group_show.append(
                    dict(cabin=cabin, brand_type=brand_type, price_type1=i[0], price_type2=i[1], price=price))
            flight['cabin_group_show'] = cabin_group_show

        get_time = datetime.fromtimestamp(int(data.get('data').get('createTime')) / 1000)
        fb_price = int(data.get('data').get('segment')[0].get('dateFlight').get('fbasic').get('adultPrice'))
        jb_price = int(data.get('data').get('segment')[0].get('dateFlight').get('jbasic').get('adultPrice'))
        wb_price = int(data.get('data').get('segment')[0].get('dateFlight').get('wbasic').get('adultPrice'))
        yb_price = int(data.get('data').get('segment')[0].get('dateFlight').get('ybasic').get('adultPrice'))
        base_price_dict = {'头等舱': fb_price, '公务舱': jb_price, '明珠经济舱': wb_price, '经济舱': yb_price}
        for flt in l_flt:
            dep_airport_id = response.request.meta.get('dep_airport_id')
            arv_airport_id = response.request.meta.get('arv_airport_id')
            dep_date = response.request.meta.get('dep_date')
            flt_no = flt.get('flightNo')
            airplane_type = None
            for i in airplane_type_list:
                if flt.get('plane') == i.get('code'):
                    airplane_type = i.get('enName') or i.get('zhName') or i.get('code')

            dep_time = flt.get('depTime')[:2] + ':' + flt.get('depTime')[2:]
            arv_time = flt.get('arrTime')[:2] + ':' + flt.get('arrTime')[2:]
            flt_time = flt.get('timeDuringFlight')
            is_direct = True if flt.get('stopNumber') == 0 else False
            transfer_city = flt.get('stopNameZh') if flt.get('stopNumber') == 1 else None
            is_shared = True if flt.get('codeShare') == 'TRUE' else False
            share_company = self.session.query(Company).filter_by(
                prefix=flt.get('codeShareInfo')[:2]).first().company_name or flt.get('codeShareInfo')[:2] if flt.get(
                'codeShare') == 'TRUE' else None
            share_flt_no = flt.get('codeShareInfo') if flt.get('codeShare') == 'TRUE' else None
            price_list_meta = flt.get('cabin_group_show')
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
                item['price_type1'] = price_row.get('price_type1')
                item['price_type2'] = price_row.get('price_type2')
                item['price'] = int(price_row.get('price'))
                item['discount'] = 1.0 * item['price'] / base_price_dict.get(item['price_type1'])
                item['create_date'] = get_time.strftime('%Y%m%d%H%M%S')
                yield item

    def closed(self, reason):
        self.session.close()
