import urllib2, urllib, cookielib, time
from bs4 import BeautifulSoup

PENN_STATION = '8'
KEW_GARDENS = '11'
JAMAICA = '15'
LIRR_URL = 'http://lirr42.mta.info/index.php'

def getDepartures(fromStation, toStation):
    '''
    Returns a list of LIRR station departure times, destinatoins, alerts, peak/off peak
    :Parameters:
     - 'fromStation': The departure station code
     - 'toStation': The destination station code
    '''

    departures =[]  #an empty list of departures
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.79 Safari/537.1' }
    
    params={'FromStation':fromStation,
            'ToStation':toStation,
            'RequestDate':time.strftime("%m/%d/%Y"),
            'RequestTime':time.strftime("%I:%M"),
            'RequestAMPM':time.strftime("%p"),
            'sortBy':'1',
            'schedules':'Schedules'}


    data = urllib.urlencode(params)
    request = urllib2.Request(LIRR_URL, data, headers)
    response = urllib2.urlopen(request)

    cookies = cookielib.CookieJar()
    cookies.extract_cookies(response,request)

    cookie_handler= urllib2.HTTPCookieProcessor( cookies )
    redirect_handler= urllib2.HTTPRedirectHandler()
    opener = urllib2.build_opener(redirect_handler,cookie_handler)

    response = opener.open(request)
    page = response.read()
    
    #use BeautifulSoup module to parse returned LIRR page
    soup = BeautifulSoup(page)
    titleTag = soup.html.head.title
    print titleTag.string
    print soup.findAll('tr')

    for i in soup.findAll('tr', {'style':True}):
        trainParams = i.findAll('td')
        departures.append({'time':trainParams[1].string, 'peak': trainParams[11].string})
    
    for departure in departures:
        print departure['time'], departure['peak']
    return titleTag.string
    
    
getDepartures(KEW_GARDENS, PENN_STATION)