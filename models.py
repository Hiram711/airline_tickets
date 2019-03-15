from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Date, Numeric
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import create_engine
from datetime import datetime
from airline_tickets.settings import META_DB_URI
from sqlalchemy import Sequence

Base = declarative_base()


class Segment(Base):
    __tablename__ = 't_crl_segments'
    dep_airport_id = Column(Integer, ForeignKey('t_crl_airports.id'), primary_key=True)
    arv_airport_id = Column(Integer, ForeignKey('t_crl_airports.id'), primary_key=True)
    create_date = Column(DateTime, default=datetime.now)
    modify_date = Column(DateTime, default=datetime.now)
    is_available = Column(Boolean, default=True)

    def __repr__(self):
        return "<Segment(%s-%s)>" % (self.dep_airport.code, self.arv_airport.code)


class Airport(Base):
    __tablename__ = "t_crl_airports"
    # id = Column(Integer, autoincrement=True, primary_key=True)  # for mysql and sqllite
    id = Column(Integer, Sequence('airport_id_seq'), primary_key=True)  # for oracle
    code = Column(String(3), unique=True, nullable=False)
    name = Column(String(32), unique=True, nullable=False)
    city = Column(String(32))
    country = Column(String(32))
    create_date = Column(DateTime, default=datetime.now)
    modify_date = Column(DateTime, default=datetime.now)
    dep_airport = relationship('Segment', foreign_keys=[Segment.arv_airport_id],
                               backref=backref('arv_airport', lazy='joined'), lazy='dynamic',
                               cascade='all,delete-orphan')
    arv_airport = relationship('Segment', foreign_keys=[Segment.dep_airport_id],
                               backref=backref('dep_airport', lazy='joined'), lazy='dynamic',
                               cascade='all,delete-orphan')

    def __repr__(self):
        return "<Airport(%s,%s)>" % (self.code, self.name)


class PriceInfo(Base):
    __tablename__ = 't_crl_price_info'
    # id = Column(Integer, autoincrement=True, primary_key=True)  # for mysql and sqllite
    id = Column(Integer, Sequence('priceinfo_id_seq'), primary_key=True)  # for oracle
    company_id = Column(Integer, ForeignKey('t_crl_companies.id'), nullable=False)
    dep_airport_id = Column(Integer, ForeignKey('t_crl_airports.id'), nullable=False)
    arv_airport_id = Column(Integer, ForeignKey('t_crl_airports.id'), nullable=False)
    dep_date = Column(Date)
    flt_no = Column(String(16))
    airplane_type = Column(String(16))
    dep_time = Column(String(16))
    arv_time = Column(String(16))
    flt_time = Column(String(32))
    is_direct = Column(Boolean, default=True)
    transfer_city = Column(String(32))
    is_shared = Column(Boolean, default=False)
    share_company = Column(String(16))
    share_flt_no = Column(String(16))
    price_type1 = Column(String(32))
    price_type2 = Column(String(32))
    discount = Column(String(16))
    price = Column(Numeric(10, 2))
    create_date = Column(DateTime, nullable=False)


class Company(Base):
    __tablename__ = 't_crl_companies'
    # id = Column(Integer, autoincrement=True, primary_key=True)  # for mysql and sqllite
    id = Column(Integer, Sequence('company_id_seq'), primary_key=True)  # for oracle
    company_name = Column(String(40), index=True, unique=True)
    prefix = Column(String(10), index=True, unique=True)
    create_time = Column(DateTime, default=datetime.now)
    modify_time = Column(DateTime, default=datetime.now)
    prices = relationship('PriceInfo', backref='company', lazy='dynamic')

    @staticmethod
    def insert_companies():
        companies = {'东方航空': 'MU',
                     '祥鹏航空': '8L',
                     '昆明航空': 'KY',
                     '南方航空': 'CZ',
                     '四川航空': '3U',
                     '春秋航空': '9C'}
        session = DBSession()
        for i in companies:
            if session.query(Company).filter_by(prefix=companies[i]).first():
                continue
            company = Company(company_name=i)
            company.prefix = companies[i]
            session.add_all([company])
            session.commit()
            session.close()

    def __repr__(self):
        return "<Company(%s,%s)>" % (self.prefix, self.company_name)


class Option(Base):
    __tablename__ = 't_crl_options'
    # id = Column(Integer, autoincrement=True, primary_key=True)  # for mysql and sqllite
    id = Column(Integer, Sequence('option_id_seq'), primary_key=True)  # for oracle
    name = Column(String(40), unique=True)
    value = Column(Integer)

    @staticmethod
    def insert_options():
        # set how many days after current date the crawler will search for
        session = DBSession()
        crawler_days = Option(name='crawler_days', value=7)
        session.add_all([crawler_days])
        session.commit()
        session.close()


class RmHnairLowestPrice(Base):
    __tablename__ = 't_crl_rmhnair_lowest_price'
    # id = Column(Integer, autoincrement=True, primary_key=True)  # for mysql and sqllite
    id = Column(Integer, Sequence('rmhna_price_id_seq'), primary_key=True)  # for oracle
    ALARM_CLS = Column(String(40))
    BOOKED = Column(String(40))
    BOOKED_RATE = Column(String(40))
    CLS_TYPE_CLASS = Column(String(40))
    CLS_TYPE_CODES = Column(String(40))
    CLS_TYPE_PRICES = Column(String(40))
    DEP_TIME = Column(String(40))
    DIFF_LF = Column(String(40))
    EX_TIME_AV = Column(String(40))
    EX_TIME_RBL = Column(String(40))
    FLIGHT_DATE = Column(String(40))
    FLIGHT_DATE_TRUE = Column(String(40))
    FLIGHT_NO = Column(String(40))
    FY_BOOKED = Column(String(40))
    FY_MAX_OPEN = Column(String(40))
    INCREMENTS = Column(String(40))
    LOWEST_PRICE = Column(String(40))
    LOWEST_STATUS = Column(String(40))
    MAX_OPEN = Column(String(40))
    NONSTOP = Column(String(40))
    WIDTH_TYPE = Column(String(40))
    OPEN_CLS = Column(String(80))
    PLANE_TYPE = Column(String(40))
    SEGMENT_CN = Column(String(40))
    SEGMENT_EN = Column(String(40))
    STATUS = Column(String(40))
    STATUS_SET = Column(String(40))
    TOMORROW_LF = Column(String(40))
    create_date = Column(String(40))


engine = create_engine(META_DB_URI)
DBSession = sessionmaker(bind=engine)

if __name__ == '__main__':
    # 删除表
    Base.metadata.drop_all(engine)
    # 创建表
    Base.metadata.create_all(engine)
    Option.insert_options()
    Company.insert_companies()
    # 插入测试数据
    session = DBSession()
    a1 = Airport(code='KMG', name='昆明长水机场', city='昆明', country='中国')
    a2 = Airport(code='CTU', name='成都双流机场', city='成都', country='中国')
    a3 = Airport(code='SHA', name='上海虹桥机场', city='上海', country='中国')
    a4 = Airport(code='HAK', name='海口美兰机场', city='海口', country='中国')
    session.add_all([a1, a2, a3, a4])
    session.commit()
    s1 = Segment(dep_airport=a1, arv_airport=a2)
    s2 = Segment(dep_airport=a1, arv_airport=a3)
    s3 = Segment(dep_airport=a1, arv_airport=a4)
    s4 = Segment(dep_airport=a2, arv_airport=a3)
    s5 = Segment(dep_airport=a2, arv_airport=a4)
    s6 = Segment(dep_airport=a3, arv_airport=a4)
    session.add_all([s1, s2, s3, s4])
    session.commit()
    session.close()
