# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TicketItem(Item):
    collection = 'tickets'  # this attribute is used for mongodb
    company_id = Field()
    dep_airport_id = Field()
    arv_airport_id = Field()
    dep_date = Field()
    flt_no = Field()
    airplane_type = Field()
    dep_time = Field()
    arv_time = Field()
    flt_time = Field()
    is_direct = Field()
    transfer_city = Field()
    is_shared = Field()
    share_company = Field()
    share_flt_no = Field()
    price_type1 = Field()
    price_type2 = Field()
    discount = Field()
    price = Field()
    create_date = Field()


class PriceRoomItem(Item):
    checkindate = Field()
    city = Field()
    price_range = Field()
    left_rooms = Field()
    create_date = Field()
