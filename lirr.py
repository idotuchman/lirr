import urllib2, urllib, cookielib, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import html5lib

PENN_STATION = '8'
KEW_GARDENS = '11'
JAMAICA_STATION = '15'
LIRR_URL = 'http://lirr42.mta.info/index.php'

def getDepartures(url, fromStation, toStation):
    '''
    Returns a list of LIRR station departure times, peak/off peak, alerts (if any)
    :Parameters:
     - 'url': The LIRR url to be used
     - 'fromStation': The departure station code
     - 'toStation': The destination station code
    '''

    today = datetime.today()    #today's date and time
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
    request = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(request)

    cookies = cookielib.CookieJar()
    cookies.extract_cookies(response,request)

    cookie_handler= urllib2.HTTPCookieProcessor( cookies )
    redirect_handler= urllib2.HTTPRedirectHandler()
    opener = urllib2.build_opener(redirect_handler,cookie_handler)

    response = opener.open(request)
    page = response.read()
    
    #use BeautifulSoup module to parse returned LIRR page
    soup = BeautifulSoup(page, "html5lib")
    titleTag = soup.html.head.title

    for i in soup.find_all('tr', {'style':True}):
        trainParams = i.find_all('td')
        timeString = trainParams[1].string
        trainTime = datetime.strptime(timeString, "%I:%M %p")  #convert train time string into datetime object
        trainDateTime = datetime.combine(today, trainTime.time())
        if (today - trainDateTime) > timedelta(hours=12):      #check if listed time is for tomorrow, if so add one day to datetime object
            trainDateTime = trainDateTime + timedelta(days = 1)
        
        # TODO need to check for delays and skip entry if departure + delay is < -10 min from now (i.e., trains has already left, no need to display departure)
        
        departures.append({'dateTime':trainDateTime, 'time':trainParams[1].string, 'peak': trainParams[11].string})

    return departures
    
if __name__ == '__main__':
    kewDepartures = getDepartures(LIRR_URL, KEW_GARDENS, PENN_STATION)  # get list of Penn Station departures

    for kewDeparture in kewDepartures:
        kewDeparture.update({'destination': 'Penn Station'})

    jamaicaDepartures = getDepartures(LIRR_URL, KEW_GARDENS, JAMAICA_STATION)  # get list of Jamaica Station departures

    for jamaicaDeparture in jamaicaDepartures:
        jamaicaDeparture.update({'destination': 'Jamaica'})
        
    kewDepartures.extend(jamaicaDepartures)     # add Jamaica departures to Penn Station departures
    kewDepartures.sort(key = lambda departure: departure["dateTime"])    # sort list by departure time

    format = "%(time)-10s %(destination)-20s %(peak)-13s"
    print format % {'time':'Time', 'destination':'Destination', 'peak':'Peak/Off Peak'}
    print '-' * 45
    for kewDeparture in kewDepartures:
#        print kewDeparture['dateTime'].strftime("%m/%d/%y %I:%M %p")
        print format % kewDeparture