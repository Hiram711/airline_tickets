# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime

from airline_tickets.models import DBSession, PriceInfo
from pymongo import MongoClient


class SqlAlchemyPipeline:

    def open_spider(self, spider):
        self.session = DBSession()

    def process_item(self, item, spider):
        item = dict(item)  # by this way we can avoid the error that some items don't have some specific keys
        p = PriceInfo(company_id=item.get('company_id')
                      , dep_airport_id=item.get('dep_airport_id')
                      , arv_airport_id=item.get('arv_airport_id')
                      , dep_date=datetime.strptime(item.get('dep_date'), '%Y%m%d')
                      , flt_no=item.get('flt_no')
                      , airplane_type=item.get('airplane_type')
                      , dep_time=item.get('dep_time')
                      , arv_time=item.get('arv_time')
                      , flt_time=item.get('flt_time')
                      , is_direct=item.get('is_direct')
                      , transfer_city=item.get('transfer_city')
                      , is_shared=item.get('is_shared')
                      , share_company=item.get('share_company')
                      , share_flt_no=item.get('share_flt_no')
                      , price_type1=item.get('price_type1')
                      , price_type2=item.get('price_type2')
                      , discount=item.get('discount')
                      , price=item.get('price')
                      , create_date=datetime.strptime(item.get('create_date'), '%Y%m%d%H%M%S'))
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
