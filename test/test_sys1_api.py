import requests
from requests.cookies import RequestsCookieJar
import json
import js2py

r = requests.get('http://127.0.0.1:5000/rmhnair/random')
cookies = r.json()

jar = RequestsCookieJar()
for k, v in cookies.items():
    jar.set(k, v)

headers = {'Host': 'rm.hnair.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
           'Accept': '*/*',
           'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
           'Accept-Encoding': 'gzip, deflate',
           'Referer': 'http://rm.hnair.com/BI/ClassTune/WebUI/FlightTune.aspx',
           'Content-Type': 'text/plain;charset=UTF-8',
           'Connection': 'keep-alive',
           }
data1 = 'flightStaDate=2019-03-05\r\nflightEndDate=2019-03-11\r\nflightTime1=00:00\r\nflightTime2=23:59\r\nsegment=KMGHAK'
r = requests.post(
    'http://rm.hnair.com/ajax/Yeesky.EIM.Site.BI.ClassTune.AjaxClass.FlightTuneAjax,Yeesky.EIM.Site.BI.ClassTune.ashx?_method=CollectData&_session=r',
    cookies=jar, headers=headers, data=data1)

test_data = js2py.eval_js('var data=%s;var data1=JSON.stringify(data);data1' % r.text)
js_data = json.loads(test_data)
z = js_data['Tables'][1].get('Rows')
for i in z:
    print(i)
