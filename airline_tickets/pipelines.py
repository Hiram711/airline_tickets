# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from airline_tickets.models import DBSession, PriceInfo
from pymongo import MongoClient


class AirlineTicketsPipeline:

    def open_spider(self, spider):
        self.session = DBSession()

    def process_item(self, item, spider):
        p = PriceInfo(dep_airport_id=item['dep_id'], arv_airport_id=item['arv_id'], dep_date=item['dep_date'],
                      flt_no=item['flt_no'], airplane_type=item['airplane_type'], flt_tm=item['flt_tm'],
                      luxury_price=item['luxury_price'], economy_price=item['economy_price'],
                      member_price=item['member_price'])
        self.session.add(p)
        self.session.commit()

        return item

    def close_spider(self, spider):
        self.session.close()


class MongoPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_uri=crawler.settings.get('MONGO_URI'), mongo_db=crawler.settings.get('MONGO_DB'))

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    def open_spider(self, spider):
        self.conn = MongoClient(self.mongo_uri)
        self.db = self.conn[self.mongo_db]

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.db[item.collection].insert(dict(item))
        return item
