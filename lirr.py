import urllib2, urllib, cookielib, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import html5lib

PENN_STATION = ('8', 'Penn Station')
KEW_GARDENS = ('11', 'Kew Gardends')
JAMAICA_STATION = ('15', 'Jamaica')
LIRR_URL = 'http://lirr42.mta.info/index.php'

def getDepartures(url, fromStation, toStation):
    '''
    Returns a list of LIRR station departure times, destination station, peak/off peak, alerts (if any)
    :Parameters:
     - 'url': The LIRR url to be used
     - 'fromStation': A tuple containing (departure station code, departure station decription)
     - 'toStation': A tuple containing (destination station code, destintion station description)
    '''

    today = datetime.today()    #today's date and time
    departures =[]              #an empty list of departures
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.79 Safari/537.1' }
    
    params={'FromStation':fromStation[0],
            'ToStation':toStation[0],
            'RequestDate':time.strftime("%m/%d/%Y"),
            'RequestTime':time.strftime("%I:%M"),
            'RequestAMPM':time.strftime("%p"),
            'sortBy':'1',
            'schedules':'Schedules'}
    data = urllib.urlencode(params)
    try:
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
            
#TODO need to check for departure delays
            if (today - trainDateTime) < timedelta(minutes = 6):      #make sure train has not already left station (i.e., departure occured more than 6 minutes ago)
                departures.append({'dateTime':trainDateTime, 'time':trainParams[1].string, 'destination': toStation[1], 'peak': trainParams[11].string})
            
        # If departures is empty there was probably some parsing or network error    
        if (len(departures)==0): raise Exception, 'Network error (' + toStation[1] + ')'
        
    except Exception, e:
#TODO use LIRR's API call as backup 
        departures =[{'dateTime':today + timedelta(days = +1), 'time':'', 'destination': e, 'peak':''}]
    return departures
    
if __name__ == '__main__':
    kewDepartures = getDepartures(LIRR_URL, KEW_GARDENS, PENN_STATION)  # get list of Penn Station departures
    
    kewDepartures.extend(getDepartures(LIRR_URL, KEW_GARDENS, JAMAICA_STATION))     # add Jamaica departures to Penn Station departures
    
    kewDepartures.sort(key = lambda departure: departure["dateTime"])    # sort list by departure time

    format = "%(time)-10s %(destination)-20s %(peak)-13s"
    print format % {'time':'Time', 'destination':'Destination', 'peak':''}
    print '-' * 40
    for kewDeparture in kewDepartures:
#        print kewDeparture['dateTime'].strftime("%m/%d/%y %I:%M %p")
        print format % kewDeparture
        
        