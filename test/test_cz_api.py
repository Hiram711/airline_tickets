import requests
import random
import json
from urllib import parse


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
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
    'flightDate': '20190301',
    'flyType': 0,
    'infantNum': '0',
    'international': '0',
    'isMember': '',
    'preUrl': '',
    'segType': '1',
}

searchParams = {
    "segType": 'S',
    "adultNum": '1',
    "childNum": '0',
    "infantNum": '0',
    "citys": [],
    "dates": []
}

cityInfo = {"id": "single-formCity", "value": '昆明'}
searchParams['citys'].append(cityInfo)
cityInfo = {"id": "single-formCityCode", "value": 'KMG'}
searchParams['citys'].append(cityInfo)
cityInfo = {"id": "single-toCity", "value": '成都'}
searchParams['citys'].append(cityInfo)
cityInfo = {"id": "single-toCityCode", "value": 'CTU'}
searchParams['citys'].append(cityInfo)
dateInfo = {"id": "single-formCalender", "value": '2019-02-22', "minDate": "+0d"}
searchParams['dates'].append(dateInfo)

searchParams = json.dumps(searchParams)
searchParams = parse.quote(searchParams)



response = requests.post(target_url, json=data, headers=get_headers(),
                         # cookies={
                         #     'zsluserCookie': 'true',
                         #     'ticketBoolingSearch': searchParams
                         # }
                         )

print(response.status_code, response.json())
