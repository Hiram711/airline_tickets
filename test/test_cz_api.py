import requests
import random


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


user_agents = [
    'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/'
    '535.11 SE 2.X MetaSr 1.0',
    'Opera/8.0 (Windows NT 5.1; U; en)',
    'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
]

target_url = 'http://b2c.csair.com/portal/flight/direct/query'


def get_headers():
    headers = {
        'Host': 'b2c.csair.com',
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json,text/javascript,*/*;q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://b2c.csair.com/B2C40/newTrips/static/main/page/booking/index.html?t=S&c1=SHA&c2=HAK&d1=2019-02-26&at=1&ct=0&it=0',
        'Connection': 'keep-alive',
    }
    return headers


data = {
    'action': '0',
    'adultNum': '1',
    'airLine': 1,
    'arrCity': 'PVG',
    'cabinOrder': '0',
    'cache': 0,
    'childNum': '0',
    'depCity': 'KMG',
    'flightDate': '20190307',
    'flyType': 0,
    'infantNum': '0',
    'international': '0',
    'isMember': '',
    'preUrl': '',
    'segType': '1',
}

response = requests.post(target_url, json=data, headers=get_headers(), )
print(response.status_code)
data = response.json()

flights = data['data']['segment'][0]['dateFlight']['flight']
for flight in flights:
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
    print(flight['flightNo'], cabin_group_show)
