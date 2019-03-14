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


class RmHnairLowestPriceItem(Item):
    ALARM_CLS = Field()
    BOOKED = Field()
    BOOKED_RATE = Field()
    CLS_TYPE_CLASS = Field()
    CLS_TYPE_CODES = Field()
    CLS_TYPE_PRICES = Field()
    DEP_TIME = Field()
    DIFF_LF = Field()
    EX_TIME_AV = Field()
    EX_TIME_RBL = Field()
    FLIGHT_DATE = Field()
    FLIGHT_DATE_TRUE = Field()
    FLIGHT_NO = Field()
    FY_BOOKED = Field()
    FY_MAX_OPEN = Field()
    INCREMENTS = Field()
    LOWEST_PRICE = Field()
    LOWEST_STATUS = Field()
    MAX_OPEN = Field()
    NONSTOP = Field()
    WIDTH_TYPE = Field()
    OPEN_CLS = Field()
    PLANE_TYPE = Field()
    SEGMENT_CN = Field()
    SEGMENT_EN = Field()
    STATUS = Field()
    STATUS_SET = Field()
    TOMORROW_LF = Field()
    create_date = Field()
