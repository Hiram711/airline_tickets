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
        'Host': 'flights.ch.com',
        'User-Agent': random.choice(user_agents),
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache', }
    return headers


def run_request():
    url = 'https://flights.ch.com/Flights/SearchByTime'
    data = {
        'IsShowTaxprice': 'false',
        'Active9s': '',
        'IsJC': 'false',
        'Currency': '0',
        'SType': '0',
        'Departure': '上海',
        'Arrival': '昆明',
        'DepartureDate': '2019-03-02',
        'ReturnDate': 'null',
        'IsIJFlight': 'false',
        'IsBg': 'false',
        'IsEmployee': 'false',
        'IsLittleGroupFlight': 'false',
        'SeatsNum': '1',
        'ActId': '0',
        'IfRet': 'false',
        'IsUM': 'false',
        'CabinActId': 'null',
        'isdisplayold': 'false',
    }

    response = requests.post(url, data=data, headers=get_headers(), timeout=10)
    res = response.text
    return res


if __name__ == '__main__':
    response = run_request()
    # print(response)
    data = json.loads(response)
    flts = data.get('Route')
    for flt in flts:
        if len(flt) > 1:  # when the result is connecting flights,ignore this result
            continue
        flt = flt[0]
        airplane_type = flt.get('Type')
        flt_time = flt.get('FlightsTime')
        flt_no = flt.get('No')
        dep_airport_code = flt.get('DepartureAirportCode')
        dep_time = flt.get('DepartureTimeBJ')[11:16]
        arv_airport_code = flt.get('ArrivalAirportCode')
        arv_time = flt.get('ArrivalTimeBJ')[11:16]
        yb_price = flt.get('Price') * 100
        cabins = flt.get('AircraftCabins')
        for cabin in cabins:
            cabin_infos = cabin.get('AircraftCabinInfos')
            cabin_level = cabin.get('CabinLevel')
            for cabin_info in cabin_infos:
                cabin_class = cabin_info.get('Name')
                cabin_price = cabin_info.get('Price')
                cabin_remain = cabin_info.get('Remain')
                print(flt_no, dep_airport_code, arv_airport_code, flt_time, airplane_type,
                      cabin_level, cabin_class, cabin_price)
