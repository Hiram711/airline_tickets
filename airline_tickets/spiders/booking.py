import scrapy
from models import DBSession
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from scrapy_splash.request import SplashRequest
from airline_tickets.items import PriceRoomItem

script = """
function main(splash, args)
  splash.images_enabled = false
  splash:set_user_agent(args.user_agent)
  splash:set_custom_headers({
   ["Host"] = "www.booking.com",
   ["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
   ["Cookie"] = "lastSeen=0",
   })
  splash:go(args.url)
  splash:wait(args.wait)
  return splash:html()
end
"""


class BookingSpider(scrapy.Spider):
    name = 'BookingHotel'

    # use splash to crawl without proxy
    custom_settings = {
        'USE_PROXY_DEFAULT': False,
        'ITEM_PIPELINES': {},  # todo write the pipline for hotel rooms counts in different price ranges
    }

    def __init__(self):
        super(BookingSpider, self).__init__()
        self.session = DBSession()
        self.origin_url = 'https://www.booking.com/searchresults.zh-cn.html?ss={}&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&no_rooms=1&group_adults=2&group_children=0'

    def start_requests(self):
        cities = ['普吉', '纽约', '伦敦']
        now = datetime.now()
        add_days = 4
        for city in cities:
            for i in range(add_days):
                checkindate = now + timedelta(days=i)
                checkoutdate = now + timedelta(days=i + 1)
                url = self.origin_url.format(city, checkindate.year, checkindate.month, checkindate.day,
                                             checkoutdate.year, checkoutdate.month, checkoutdate.day)
                yield SplashRequest(url, self.parse, endpoint='execute',
                                    args={
                                        'lua_source': script,
                                        'wait': 5
                                    },
                                    meta={'city': city, 'date': checkindate.strftime('%Y%m%d')})

    def parse(self, response):
        create_date = datetime.now().strftime('%Y%m%d%H%M%S')
        soup = BeautifulSoup(response.text, 'html5lib')
        price_filter = soup.select_one('#filter_price')
        if not price_filter:
            self.logger.debug('Please check this url:%s' % response.url)
            return
        price_boxes = price_filter.select('.barrel_o_filters .filterelement')
        for price_box in price_boxes:
            item = PriceRoomItem()
            price_info = price_box.find_all('span')
            left_rooms = price_info[1].text.strip()
            price_range = price_info[0].text.strip()
            item['checkindate'] = response.meta.get('date')
            item['city'] = response.meta.get('city')
            item['price_range'] = price_range
            item['left_rooms'] = left_rooms
            item['create_date'] = create_date
            yield item

    def closed(self, reason):
        self.session.close()
