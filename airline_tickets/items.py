# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TicketsItemMU(Item):
    collection = 'tickets'
    company = Field()
    flt_no = Field()
    airplane_type = Field()
    flt_tm = Field()
    luxury_price = Field()
    economy_price = Field()
    member_price = Field()
    dep_date = Field()
    dep_id = Field()
    arv_id = Field()
