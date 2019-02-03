# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from airline_tickets.models import DBSession, PriceInfo


class AirlineTicketsPipeline(object):

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
