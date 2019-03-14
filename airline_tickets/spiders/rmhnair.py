import scrapy
import js2py
import json
from datetime import datetime, timedelta
from airline_tickets.models import DBSession, Segment, Option
from airline_tickets.items import RmHnairLowestPriceItem


class RmHnairSpider(scrapy.Spider):
    name = 'rmhnair'
    custom_settings = {
        'RMHNAIR_ADD_DAYS': 7,
        'RMHNAIR_ADD_TIMES': 4,
        'COOKIES_URL': 'http://10.42.11.226:5020/rmhnair/random',
        'SPIDER_MIDDLEWARES': {},  # disable splash
        'DOWNLOADER_MIDDLEWARES':
            {
                'airline_tickets.middlewares.CookiesMiddleware': 553,
            },
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',  # disable splash and using default setting
        'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',
        'ITEM_PIPELINES': {'airline_tickets.pipelines.RmHnairSqlAlchemyPipeline': 300, },
    }

    def __init__(self):
        super(RmHnairSpider, self).__init__()
        self.session = DBSession()
        self.url = 'http://rm.hnair.com/ajax/Yeesky.EIM.Site.BI.ClassTune.AjaxClass.FlightTuneAjax,Yeesky.EIM.Site.BI.ClassTune.ashx?_method=CollectData&_session=r'
        self.data_str = 'flightStaDate={}\r\nflightEndDate={}\r\nflightTime1=00:00\r\nflightTime2=23:59\r\nsegment={}'
        self.headers = {'Host': 'rm.hnair.com',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
                        'Accept': '*/*',
                        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                        'Accept-Encoding': 'gzip, deflate',
                        'Referer': 'http://rm.hnair.com/BI/ClassTune/WebUI/FlightTune.aspx',
                        'Content-Type': 'text/plain;charset=UTF-8',
                        'Connection': 'keep-alive',
                        }

    def start_requests(self):
        date_add = self.settings.get('RMHNAIR_ADD_DAYS') or 7
        date_add_times = self.settings.get('RMHNAIR_ADD_TIMES') or 4
        segments = self.session.query(Segment).filter_by(is_available=True).all()
        now = datetime.now()
        for segment in segments:
            for i in range(0, date_add_times):
                dep_city = segment.dep_airport.code.upper()
                arv_city = segment.arv_airport.code.upper()
                begin_date_str = (now + timedelta(days=i * date_add)).strftime('%Y-%m-%d')
                end_date_str = (now + timedelta(days=((i + 1) * date_add - 1))).strftime('%Y-%m-%d')
                data = self.data_str.format(begin_date_str, end_date_str, dep_city + arv_city)
                yield scrapy.Request(self.url, callback=self.parse, method='POST', headers=self.headers, body=data,
                                     meta={'dep_airport_id': segment.dep_airport.id,
                                           'arv_airport_id': segment.arv_airport.id, })

    def parse(self, response):
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        receive_data = js2py.eval_js('var data=%s;var data1=JSON.stringify(data);data1' % response.text)
        json_data = json.loads(receive_data)
        for row in json_data['Tables'][1].get('Rows'):
            item = RmHnairLowestPriceItem()
            for k, v in row.items():
                if k == 'NVL(RPT.WIDTH_TYPE,0)':
                    item['WIDTH_TYPE'] = v
                else:
                    item[k] = v
            item['create_date'] = now
            yield item
