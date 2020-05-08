#
# races.py - this builds on the MEC capability and Met Office
# to provide a summary of up coming races along with a weather forecast
#
# It does three things
#   find the events within the next 7 days (limited to met office forecast)
#   and extracts the event details - which have duty and tides for now
#   gets the met office 3 hour forecats for the period
#   constructs and sends an email - racing@ranelaghsc.co.uk
#
# Distributed under MIT License
# 
# Copyright (c) 2020 Greg Brougham
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# imports
import os   # for environ()
import sys, getopt
import requests
import geojson  # the structure for the data
import http.client  # redundant as using requests
#import datetime
from datetime import datetime, timezone
# following needs backports-datetime-fromisofromat to be intalled on 3.5
if sys.version_info < (3, 6):
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()
from lxml import html
#from datetime import date
import dateutil.relativedelta
from dateutil import parser
from bs4 import BeautifulSoup

# for email
import smtplib
from email.mime.text import MIMEText
import dutymand # for getDuties and dutyList
from creds import *

FLOODTIDE = 7.2


# for met office significant weather
Weather = [
    "Clear night",
    "Sunny day",
    "Partly cloudy (night)",
    "Partly cloudy (day)",
    "Not used",
    "Mist",
    "Fog",
    "Cloudy",
    "Overcast",
    "Light rain shower (night)",
    "Light rain shower (day)",
    "Drizzle",
    "Light rain",
    "Heavy rain shower (night)",
    "Heavy rain shower (day)",
    "Heavy rain",
    "Sleet shower (night)",
    "Sleet shower (day)",
    "Sleet",
    "Hail shower (night)",
    "Hail shower (day)",
    "Hail",
    "Light snow shower (night)",
    "Light snow shower (day)",
    "Light snow",
    "Heavy snow shower (night)",
    "Heavy snow shower (day)",
    "Heavy snow",
    "Thunder shower (night)",
    "Thunder shower (day)",
    "Thunder" ]


# compass direction for the wind direction summary
compass = ["N","NNE","NE",
            "ENE","E","ESE",
            "SE","SSE","S",
            "SSW","SW","WSW","W",
            "WNW","NW","NNW","N"]

def windDir(dir):
    global compass

    direction = ""

    direction = compass[int(round(dir/22.5, 0))]

    return direction

# end windDir


#
# email results file to defined recipent
def sendRaces(races):
    #
    #g_mail_recipent = 'integ@ranelaghsc.co.uk'
    g_mail_recipent = 'racing@ranelaghsc.co.uk'
    fromaddr = 'ranelaghscapp@gmail.com'
    subject = "Forthcoming club races"
    raceday = datetime.now().strftime("%d %b %Y")
    #raceday = datetime.datetime.now().strftime("%d %b %Y")

    # Credentials (injected via creds.py)
    username = eusername
    password = epassword

    msg = MIMEText(races)

    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = g_mail_recipent # from the conf file


    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    #server.sendmail(fromaddr, toaddr, message)
    server.send_message(msg)
    server.close()
# end of sendRaces()


def mectodate(date, hour, mins, ampm):

    if (ampm == "PM" and hour < 12):
        hour = hour + 12

    # now format the iso string
    estart = "{}T{:02d}:{:02d}".format(date, int(hour), int(mins))
    # and then parse to date for return
    tdate = parser.isoparse (estart)

    return tdate
# end mectodate


# The main access url for the wordpress post api
siteurl = "https://ranelaghsc.co.uk/"
eventsurl = "https://ranelaghsc.co.uk/wp-json/wp/v2/mec-events"
mecurl = siteurl + "wp-json/mecexternal/v1/calendar/1778"
# the events list
events =["", "", "", ""]
eventCnt = 0

#
# get the MEC events
#
def loadEvents ():
    global events, eventCnt, eventsurl, mecurl

    eventCnt = 0
    # note the current date & calc yesterday
    tnow = datetime.now()
    #tnow = datetime.datetime.now()
    # days = 6.5 is probably a sensible limit
    forecastLimit = tnow + dateutil.relativedelta.relativedelta(days=6.5)
    #forecastLimit = tnow + dateutil.relativedelta.relativedelta(days=6.8)
    #tquery = ptime.isoformat()
    #print (tnow, forecastLimit)

    # do the request - limted to '3' - need to increase to 8
    # note we can sort by event date as it is not exposed!


    # increased to 15 with feb/mar loaded
    #reqstr = eventsurl + "?per_page=15&order=desc"
    try:
        req = requests.get(mecurl)
    except Exception as e:
        print ("Error on requests():", sys.exc_info()[0])
        return eventCnt

    if (req.status_code != 200):
        logging.error("events return not 200")
        return eventCnt

    pdict = req.json()
    noEvents = len(req.json())
    #print (noEvents)

    jdict = pdict["content_json"] # this is actually the data
    # now query mec-event end point
    for x in jdict:
        #id = jdict[x]['id']

        # get the actual event record
        #mecreq = requests.get(mecurl + str(id))
        #if (mecreq.status_code != 200):
            #logging.error("mecreq return not 200")
            #return 0

        for y in jdict[x]: # this at the date or individual level
            #mecdict = mecreq.json()

            #tdate = y['meta']['mec_date']['start']['date']
            #thour = y['meta']['mec_date']['start']['hour']
            #tmins = y['meta']['mec_date']['start']['minutes']
            #tampm = y['meta']['mec_date']['start']['ampm']

            #stitle = y["data"]["title"]
            #scontent = y["data"]["content"]

            tdate = y["data"]["meta"]["mec_start_date"]
            thour = y["data"]["meta"]["mec_start_time_hour"]
            tmins = y["data"]["meta"]["mec_start_time_minutes"]
            tampm = y["data"]["meta"]["mec_start_time_ampm"]

            # get a date object
            prdate = mectodate(tdate, int(thour), int(tmins), tampm)
            #print (prdate, tnow, forecastLimit)
            #if (prdate > tnow):
            if (prdate <= forecastLimit and eventCnt < 4):
                #events[3] = events[2]
                #events[2] = events[1]
                #events[1] = events[0]
                events[eventCnt] = y["data"]

                eventCnt = eventCnt + 1
        # end data
    # end entries

    return eventCnt # the 0-4 events we've found
# end of loadEvents

timeseries = ""
# return the timeseries entry that is relevant
def timeIndex(rdate):
    global timeseries

    for x in range (len(timeseries)):
        if (raceStart < timeseries[x]['time']):
            break

    # we don't need move back one as this is the weather for the previous
    # three hours
    return timeseries[x - 1]
    #return timeseries[x]

# end timeIndex

def removeNonAscii(s): return "".join(i for i in s if (ord(i)<128 and ord(i)>31))

#tidelist = []
tideurl = "http://thamestides.org.uk/dailytides2.php?statcode=PUT&startdate="

# get the tides for the given date
def getTides(tdate):
    # build the url and get the entry

    dt = datetime.fromisoformat(tdate)
    sdate = str(int(dt.replace(tzinfo=timezone.utc).timestamp()))
    #print(sdate)

    tidelist = [] # truncate
    dayurl = tideurl + sdate

    page = requests.get(dayurl) # get the day entry
    if (page.status_code != 200):
        print ("Error on dayurl")

    tree = html.fromstring(page.content)

    """
    items = []
    #print (len(items))
    if (len(items) == 0): # then initialise
        for j in range(4, 4 + 5): # should be 4 - 8
            column = []
            for i in range(1,6):
                column.append("")
            items.append(column)
    # now initialised
    #print (len(items))
    """

    entry = ["", "", "", "", ""] # array of 5 items
    # now parse the table into the array - note doesn't error
    for row in range (4, 4 + 5):
        for col in range(1,6):
            # returns list
            item = tree.xpath('//table[@class="first"]//tr['
                        + str(row) + ']//td[' + str(col) + ']//text()')
            if (len(item) > 0):
                #items[row-4][col-1] = item[0]
                #items[row-4][col-1] = removeNonAscii(item[0])
                entry[col-1] = removeNonAscii(item[0])
            else:
                #items[row-4][col-1] = ""
                entry[col-1] = ""
            #print ("items ", str(row), str(col), items[row-4][col-1])

        # for
        tide = {'type': str(entry[0]), 'time': entry[1], 'height': entry[2]}
        tidelist.append(tide)
    # for

    return tidelist
# end getTides()


unixOptions = "m" # allow '-m' for no email to support testing

# main section
#
# retrieve the access keys from the environment
met_id = os.environ.get('MET_ID')
met_key = os.environ.get('MET_KEY')

if (met_id == "" or met_key == ""):
    print ("Please set MET_ID and MET_KEY")
    exit(1)

# parse command line
noMail = False
fullArgs = sys.argv
argList = fullArgs[1:]
args, values = getopt.getopt(argList, "m", "mail")
for currArg, currVal in args:
    if (currArg == "-m"):
        noMail = True


# xxx
# get flood dates for the next week
floods = [] # truncate
for day in [1, 2, 3, 4, 5 , 6, 7]:
    fdate = datetime.now() + dateutil.relativedelta.relativedelta(days=day)
    tdate = fdate.strftime("%Y-%m-%d")
    #print (day, tdate, fdate)

    tides = getTides(tdate) # "YYYY-MM-DD"
    #print (tides)
    for tide in tides:
        theight = tide['height']
        #print (" > ", theight)
        if (len(theight) > 1 and float(theight) >= FLOODTIDE):
            #print ("Flood ", theight)
            flood = {'date': fdate, 'time': tide['time'], 'height': theight}
            floods.append(flood)
        #     append floods
    # end tides
# end for

# initialise the dutyman & get the duties list - add rosterid?
dutyman = dutymand.DutyMan()
duties = dutyman.getDuties(RosterId)

meturl = "https://api-metoffice.apiconnect.ibmcloud.com"
conn = http.client.HTTPSConnection("api-metoffice.apiconnect.ibmcloud.com")

headers = {
    'x-ibm-client-id': met_id,
    'x-ibm-client-secret': met_key,
    'accept': "application/json"
    }

# lat/long are the figures from the windguru custom location for the club
metreq = "/metoffice/production/v0/forecasts/point/three-hourly?excludeParameterMetadata=false&includeLocationName=true&latitude=51.469&longitude=-0.2199"
#metreq = "/metoffice/production/v0/forecasts/point/hourly?excludeParameterMetadata=false&includeLocationName=false&latitude=51.469&longitude=-0.2199"

# use requests to retrieve the forecast
try:
    req = requests.get(meturl + metreq, headers=headers)
except Exception as e:
    print ("Error on requests():", sys.exc_info()[0])
    exit(1)

if (req.status_code != 200):
    print ("Error getting forecasts", req.status_code)
    exit (1)

#print (req.json())

#rgeo = geojson(req.text)
rdict = req.json()

# the lenght is 3 as there are 3 blocks: type, features and parameters
#print (len(rdict))

#for x in range(len(rdict)):
#    print (rdict[x][0])

x = 0
for feature in rdict['features']:
    #print ("Loop: ", x)
    #print (feature['properties']['modelRunDate'])
    timeseries = feature['properties']['timeSeries']
    #print (feature['properties']['location']['name'])
    x = x + 1

# now load the events
cnt = loadEvents()
raceEvents = events # the global
if (cnt == 1):
    print ("We have {} race coming up:\n".format(cnt))
    races = "We have {} race coming up:\n\n".format(cnt)
else:
    print ("We have {} races coming up:\n".format(cnt))
    races = "We have {} races coming up:\n\n".format(cnt)

for x in range(cnt): # for the 0-4 races ...
    #print (raceEvents[x])
    #print ("> ", raceEvents[x]['ID'], " ",
        #raceEvents[x]['post']['post_title'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['date'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['hour'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['minutes'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['ampm'])

    #tdate = raceEvents[x]['meta']['mec_date']['start']['date']
    #thour = raceEvents[x]['meta']['mec_date']['start']['hour']
    #tmins = raceEvents[x]['meta']['mec_date']['start']['minutes']
    #tampm = raceEvents[x]['meta']['mec_date']['start']['ampm']
    tdate = raceEvents[x]["meta"]["mec_start_date"]
    thour = raceEvents[x]["meta"]["mec_start_time_hour"]
    tmins = raceEvents[x]["meta"]["mec_start_time_minutes"]
    tampm = raceEvents[x]["meta"]["mec_start_time_ampm"]

    # get a date object
    prdate = mectodate(tdate, int(thour), int(tmins), tampm)

    hr = int(thour)
    if (hr < 12 and tampm == "PM"): hr = hr + 12
    #rtime = str("{}:{}".format(hr, int(tmins)
    rtime = "{:02d}:{:02d}".format(int(hr), int(tmins))
    # type, time, hieght = gettide(date, hr, mins)

    tides = getTides(tdate) # "YYYY-MM-DD"

    #print (rtime)
    tnote = ""
    for tide in tides:
        if (tide['time'] > rtime):
            ttype = tide['type']
            ttime = tide['time']
            theight = tide['height']
            if (float(theight) >= 7.0):
                tnote = " water will be across the road"
            break

    #print (tide, ttype, ttime, theight)

    # This is the event time
    #raceStart = "2020-01-12T14:30"
    #evdate = parser.isoparse(raceStart)
    raceStart = prdate.isoformat()

    #print (raceStart)

    # get the timeseries entry for the weather
    tentry = timeIndex(raceStart)
    #print (tentry['time'])

    # and the list of duties
    dutylist = dutyman.dutyList(tdate) # isodate
    #print (dutylist)

    econtent = raceEvents[x]['content']
    #etitle = mecevents[x]['post']['post_title']
    cleantext = BeautifulSoup(econtent, "lxml").text
    cleantext = cleantext[0:-1] # remove '\n'

    raceTitle = BeautifulSoup(raceEvents[x]['title'], "lxml").text
    #raceTitle = raceEvents[x]['title']
    #raceTitle = raceEvents[x]['title']
    windSpeed = round(tentry['windSpeed10m'] * 1.943844, 1)
    windGust = round(tentry['windGustSpeed10m'] * 1.943844, 1)
    windNo = int(tentry['windDirectionFrom10m'])
    windDirect = windDir(int(tentry['windDirectionFrom10m']))
    probOfRain = tentry['probOfRain']
    probOfPrec = tentry['probOfPrecipitation']
    visibility = tentry['visibility']
    feelsLike = int(tentry['feelsLikeTemp'])
    signW = Weather[int(tentry['significantWeatherCode'])]
    #signW = Weather[wcode]

    if (x > 0):
        print ('')
        races = races + "\n"
    #print (f'{raceTitle}, {prdate:%a %d %b @ %H:%M}')
    print ("{}, {:%a %d %b @ %H:%M}".format(raceTitle, prdate))
    #print ('{}'.format(cleantext))
    print ('{}'.format(dutylist))
    print ("Tide " + tide['type'] + " at " + tide['time'] + ", height " + tide['height'])
    #print (f'Wind {windDirect} ({windNo}), {windSpeed} kts, gusting {windGust} kts')
    print ("Wind {} ({}), {} kts, gusting {} kts".format(windDirect, windNo, windSpeed, windGust))
    #print (f'and {signW}, temperature {feelsLike}C, with {probOfPrec}% probability of rain')
    print ("and it will be {}, temperature {}C, with {}% probability of rain".format(signW, feelsLike, probOfPrec))

    #races = races + "We have {1} races coming up:\n\n".format(cnt)
    races = races + "{}, {:%a %d %b @ %H:%M}\n".format(raceTitle, prdate)
    #races = races + cleantext + "\n"
    races = races + dutylist + "\n"
    races = races + "Tide " + tide['type'] + " at " + \
                            tide['time'] + ", height " + tide['height'] + "\n"
    races = races + "Wind {} ({}), {} kts, gusting {} kts".format(windDirect, windNo, windSpeed, windGust)
    races = races + " and it will be {}, temperature {}C, with {}% probability of rain\n".format(signW, feelsLike, probOfPrec)
    # end dispaly the races

# add tide heights if > 6.9m when flooding is likely
fmsg = "The club is likely to flood on the following tides:"
if len(floods) > 0:
    if (cnt > 0):
        fmsg = "\n" + fmsg
    print(fmsg)
    races = races + fmsg + "\n"
    for flood in floods:
        # {'type': tide['type'], 'time': tide['time'], 'height': theight}
        tdate = flood['date'].strftime("%a %d %b %Y")
        tstr = "{} @ {} ({})".format(tdate, flood['time'], flood['height'])
        print (tstr)
        races = races + tstr + "\n"
    # end floods
# end of if floods

if (noMail == False): # email by default
    sendRaces(races)
else:
    print ("No email sent")


# we need to step thru the timeseries and find the entry for the race date/time

#visibility - number of metres - 26007
#probOfPrecipitation
#uvIndex
#significantWeatherCode 7


# end of file
