import urllib2, urllib, cookielib, time
from bs4 import BeautifulSoup

PENN_STATION = '8'
KEW_GARDENS = '11'

headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.79 Safari/537.1' }
url = 'http://lirr42.mta.info/index.php'
params={'FromStation':PENN_STATION,
        'ToStation':KEW_GARDENS,
        'RequestDate':time.strftime("%m/%d/%Y"),
        'RequestTime':time.strftime("%I:%M"),
        'RequestAMPM':time.strftime("%p"),
        'sortBy':'1',
        'schedules':'Schedules'}


data = urllib.urlencode(params)
request = urllib2.Request(url, data, headers)
response = urllib2.urlopen(request)

cookies = cookielib.CookieJar()
cookies.extract_cookies(response,request)

cookie_handler= urllib2.HTTPCookieProcessor( cookies )
redirect_handler= urllib2.HTTPRedirectHandler()
opener = urllib2.build_opener(redirect_handler,cookie_handler)

response = opener.open(request)
page = response.read()

fileObj = open('D:/LIRR/test.html','w') # open for write
fileObj.write(page)
fileObj.close()

# use beautiful soup to parse HTML
soup = BeautifulSoup(page)
print soup.prettify()