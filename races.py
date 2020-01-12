#
#
#

import os   # for environ()
import requests
import geojson  # the structure for the data
import http.client  # redundant as using requests
import datetime
#from datetime import date
import dateutil.relativedelta
from dateutil import parser
from bs4 import BeautifulSoup


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


compass = ["N","NNE","NE",
            "ENE","E","ESE",
            "SE","SSE","S",
            "SSW","SW","WSW","W",
            "WNW","NW","NNW","N"]

def windDir(dir):
    global compass

    direction = ""

    direction = compass[int(round(dir/22.5, 0)) + 1]
    #if (dir > and dir < 11):
        #direction = "N"
    #elif (dir > 11 and dir < xxx):
        #direction = "NNE"

    return direction

# end windDir

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
mecurl = siteurl + "wp-json/mecexternal/v1/event/"
# the events list
events =["", "", ""]
eventCnt = 0

#
# get the MEC events
#
def loadEvents ():
    global events, eventCnt, eventsurl, mecurl

    eventCnt = 0
    # note the current date & calc yesterday
    tnow = datetime.datetime.now()
    # days = 6.5 is probably a sensible limit
    forecastLimit = tnow + dateutil.relativedelta.relativedelta(days=6.8)
    #tquery = ptime.isoformat()
    #print (tnow, forecastLimit)

    # do the request - limted to '3' - need to increase to 8
    # note we can sort by event date as it is not exposed!
    reqstr = eventsurl + "?per_page=10&order=desc"
    req = requests.get(reqstr)
    if (req.status_code != 200):
        logging.error("events return not 200")
        return eventCnt

    jdict = req.json()
    noEvents = len(req.json())
    #print (noEvents)

    # now query mec-event end point
    for x in range(len(jdict)):
        id = jdict[x]['id']

        # get the actual event record
        mecreq = requests.get(mecurl + str(id))
        if (mecreq.status_code != 200):
            logging.error("mecreq return not 200")
            return 0

        mecdict = mecreq.json()

        tdate = mecdict['meta']['mec_date']['start']['date']
        thour = mecdict['meta']['mec_date']['start']['hour']
        tmins = mecdict['meta']['mec_date']['start']['minutes']
        tampm = mecdict['meta']['mec_date']['start']['ampm']

        # get a date object
        prdate = mectodate(tdate, thour, tmins, tampm)
        #print (prdate, tnow, forecastLimit)
        if (prdate > tnow):
            if (prdate < forecastLimit):
                events[2] = events[1]
                events[1] = events[0]
                events[0] = mecdict

                eventCnt = eventCnt + 1

                #print ("found event", eventCnt)

                #events[0] = events[1]
                #events[1] = events[2]
                #events[2] = mecdict
        else:
            break

    # end for

    return eventCnt # the 3 events we've found
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


# main section
#
# retrieve the access keys from the environment
met_id = os.environ.get('MET_ID')
met_key = os.environ.get('MET_KEY')

if (met_id == "" or met_key == ""):
    print ("Please set MET_ID and MET_KEY")
    exit(1)

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
req = requests.get(meturl + metreq, headers=headers)
#print (req.status_code)
if (req.status_code != 200):
    print ("Error getting forecasts")
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
print (f"We have {cnt} races coming up:\n")

for x in range(cnt):
    #print (raceEvents[x])
    #print ("> ", raceEvents[x]['ID'], " ",
        #raceEvents[x]['post']['post_title'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['date'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['hour'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['minutes'], " ",
        #raceEvents[x]['meta']['mec_date']['start']['ampm'])

    tdate = raceEvents[x]['meta']['mec_date']['start']['date']
    thour = raceEvents[x]['meta']['mec_date']['start']['hour']
    tmins = raceEvents[x]['meta']['mec_date']['start']['minutes']
    tampm = raceEvents[x]['meta']['mec_date']['start']['ampm']

    # get a date object
    prdate = mectodate(tdate, thour, tmins, tampm)

    # This is the event time
    #raceStart = "2020-01-12T14:30"
    #evdate = parser.isoparse(raceStart)
    raceStart = prdate.isoformat()

    #print (raceStart)

    # get the timeseies entry for the weather
    tentry = timeIndex(raceStart)
    #print (tentry['time'])

    econtent = raceEvents[x]['content']
    #etitle = mecevents[x]['post']['post_title']
    cleantext = BeautifulSoup(econtent, "lxml").text
    cleantext = cleantext[0:-1]

    raceTitle = raceEvents[x]['post']['post_title']
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
    print (f'{raceTitle}, {prdate:%a %d %b @ %H:%M}')
    print (f'{cleantext}')
    print (f'Wind {windDirect} ({windNo}), {windSpeed} kts, gusting {windGust} kts')
    print (f'and {signW}, temperature {feelsLike}C, with {probOfPrec}% probability of rain')

    # now dispaly the races


# we need to step thru the timeseries and find the entry for the race date/time

#visibility - number of metres - 26007
#probOfPrecipitation
#uvIndex
#significantWeatherCode 7


# end
