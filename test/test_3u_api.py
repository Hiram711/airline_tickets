import requests
import random
import json

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


def get_proxy():
    response = requests.get('http://10.42.11.226:5010/get')
    proxy = response.text
    proxy = {'http': proxy, 'https': proxy}
    return proxy


def get_headers():
    headers = {
        'Host': 'flights.sichuanair.com',
        'User-Agent': random.choice(user_agents),
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    return headers


def run_request():
    url = 'http://flights.sichuanair.com/3uair/ibe/common/processSearchForm.do'
    data = {
        'Search/AirlineMode': 'false',
        'Search/calendarCacheSearchDays': '60',
        'Search/calendarSearched': 'false',
        'dropOffLocationRequired': 'false',
        'Search/searchType': 'F',
        'searchTypeValidator': 'F',
        'xSellMode': 'false',
        'Search/flightType': 'oneway',
        'destinationLocationSearchBoxType': 'L',
        'Search/isUserPrice': '1',
        'Search/OriginDestinationInformation/Origin/location': 'CITY_CKG_CN',
        'Search/OriginDestinationInformation/Origin/location_input': '重庆',
        'Search/OriginDestinationInformation/Destination/location': 'CITY_KMG_CN',
        'Search/OriginDestinationInformation/Destination/location_input': '昆明',
        'Search/DateInformation/departDate_display': '2019-03-07',
        'Search/DateInformation/departDate': '2019-03-07',
        'Search/DateInformation/returnDate': '2019-03-04',
        'Search/calendarSearch': 'false',
        'Search/Passengers/adults': '1',
        'Search/Passengers/children': '0',
        'Search/promotionCode': '',
    }

    response = requests.post(url, data=data, headers=get_headers(), timeout=10)
    res = response.text
    return res


if __name__ == '__main__':
    response = run_request()
    print(response)
