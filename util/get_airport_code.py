import requests
import random

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
        'User-Agent': random.choice(user_agents),
        'Host': 'data.variflight.com',
        'Accept': 'application/json,text/javascript,*/*;q=0.01',
        'Origin': 'https://data.variflight.com',
        'Referer': 'https://data.variflight.com/analytics/CodeQuery',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    return headers


def generate_airport_code():
    letter1 = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'A',
               'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    for i in range(0, 6):
        for j in range(0, 26):
            for k in range(0, 26):
                iata = letter1[i] + letter1[j] + letter1[k]
                yield iata


def run_request(item):
    attempts = 0
    success = False
    url = 'https://data.variflight.com/analytics/Codeapi/airportCode'
    data = {
        'key': item,
        'page': '0'
    }
    while attempts < 3 and not success:
        try:
            response = requests.post(url, proxies=get_proxy(), data=data, headers=get_headers(), timeout=10)
            res = response.json()
            msg = res.get("message")
            if msg == '查询成功':
                data = res.get("data")[0]
                return data
        except Exception as e:
            attempts += 1
            if attempts == 3:
                return None
                break
            print(e)


def get_httpbin():
    url = 'http://httpbin.org/post'
    res = requests.post(url, proxies=get_proxy(), headers=get_headers())
    print(res.text)


if __name__ == '__main__':
    # get_httpbin()
    for i in generate_airport_code():
        print(run_request(i))
