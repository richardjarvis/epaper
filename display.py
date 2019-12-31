#!/usr/bin/python3
#
# -*- coding:utf-8 -*-
import sys
import os

# need the name of root of the pic and lib directories
# they also have fonts under fonts under picdir
picdir = "./epaperws/pic"
#picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = "./epaperws/lib"
#libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2 # for the 800x600 V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

# needed for html requests
import requests
import json
import datetime
from datetime import date
import dateutil.relativedelta
from dateutil import parser
import pyowm # wraps open weather apis
from lxml import html

from bs4 import BeautifulSoup



# changed from DEBUG to INFO
logging.basicConfig(level=logging.INFO)

winddomain = "https://wind.ranelaghsc.co.uk/"
windurl = winddomain + "daywind.png"
winddirurl = winddomain + "daywinddir.png"

def loadWind ():
    r = requests.get(windurl, allow_redirects=True)
    open('./tmp/daywind-copy.png', 'wb').write(r.content)

    r2 = requests.get(winddirurl, allow_redirects=True)
    open('./tmp/daywinddir-copy.png', 'wb').write(r2.content)

    file_in = "./tmp/daywind"
    img = Image.open(file_in + "-copy.png")
    img2 = img.convert("1")
    img2.save(file_in + ".bmp")

    file_in = "./tmp/daywinddir"
    img = Image.open(file_in + "-copy.png")
    img2 = img.convert("1")
    img2.save(file_in + ".bmp")

    # end


# tide url & init tides
tideurl = 'https://thamestides.org.uk/dailytides2.php?statcode=PUT&startdate=0'
tides = []

def loadTides():
    global tideurl, tides

    norows = 4
    nocols = 5

    tidepage = requests.get(tideurl)
    tree = html.fromstring(tidepage.content)

    #print (len(tides))
    if (len(tides) == 0): # then initialise
        for j in range(4, 4 + 4): # should be 4 - 8
            column = []
            for i in range(1, 1 + 5):
                column.append("")
            tides.append(column)
    # now initialised
    #print (len(tides))

    # now parse the table into the array - note doesn't error
    for row in range (4, 4 + 4):
        for col in range(1, 1 + 5):
            tides[row-4][col-1] = tree.xpath('//table[@class="first"]//tr['
                        + str(row) + ']//td[' + str(col) + ']//text()')
            #print ("tides ", str(row), str(col), tides[row-4][col-1])
        # end for
    # end for

    # now clean the entries up
    tstr = "" # a string
    for row in range(4):
        #print (str(tides[row][0]), len(tides[row][0]))
        for col in range(5):
            if (len(tides[row][col]) > 0): # if there something in the table
                tstr = str(tides[row][col])
                tstr = tstr[1:-1] # that the [] off
                tides[row][col] = tstr.replace("'", "")
            #print (tides[row][col], "!", end='')
            #print (len(tides[row][0]))
        #print ()
        # end for
    # end for

    return (tides)
    # end loadTides()

ranelaghlogo = "./tmp/ranelagh-253x47"
# function to convert logo
def ranelaghLogo():

    file_in = ranelaghlogo
    img = Image.open(file_in + ".png")
    img2 = img.convert("1")
    img2.save(file_in + ".bmp")
    #end

#
# get the wordpress posts
#
def loadPosts ():
    # The main access url for the wordpress post api
    postsurl = "https://ranelaghsc.co.uk/wp-json/wp/v2/posts"

    # note the current date & calc the date for the last month
    tnow = datetime.datetime.now()
    ptime = tnow - dateutil.relativedelta.relativedelta(months=1)
    tquery = ptime.isoformat()

    # do the request - limted to '5'
    reqstr = postsurl + "?per_page=5&order=desc&after=" + tquery
    req = requests.get(reqstr)

    #jdict = req.json()
    #noPost = len(req.json())

    return (req.json())
    # end

#
# get the wordpress events
#
def loadEvents ():
    # The main access url for the wordpress post api
    eventsurl = "https://ranelaghsc.co.uk/wp-json/wp/v2/mec-events"

    # note the current date & calc the date for the last month
    tnow = datetime.datetime.now()
    ptime = tnow - dateutil.relativedelta.relativedelta(months=1)
    tquery = ptime.isoformat()

    # do the request - limted to '3'
    # note we can sort by event date as it is not exposed!
    reqstr = eventsurl + "?per_page=3&order=desc"
    req = requests.get(reqstr)
    jdict = req.json()
    noEvents = len(req.json())

    return (req.json())
    # end

#
# load predictions from the met office datahub
#
meturl = "https://api-metoffice.apiconnect.ibmcloud.com"
headers=""
#headers = {
    #}
metreq = "/metoffice/production/v0/forecasts/point/hourly?excludeParameterMetadata=false&includeLocationName=false&latitude=51.469&longitude=-0.2199"

def getMet ():
    global headers

    # set the headers based on the inject keys
    if (headers == ""):
        headers = {
        'x-ibm-client-id': met_id,
        'x-ibm-client-secret': met_key,
        'accept': "application/json"
    }
    req = requests.get(meturl + metreq, headers=headers)
    #print (req.status_code)

    #rgeo = geojson(req.text)
    rdict = req.json()

    # trick to get a timeseries 'dict'
    for feature in rdict['features']:
        #print ("Loop: ", x)
        #print (feature['type'])
        #print (feature['geometry']['type'])
        #print (feature['geometry']['coordinates'])
        #print (feature['properties']['requestPointDistance'])
        #print (feature['properties']['modelRunDate'])
        timeseries = feature['properties']['timeSeries']

    # return timeseries dict
    return (timeseries)
    #end


# convert MEC attritubutes to ISO and parse to a date object.
def mectodate(date, hour, mins, ampm):

    if (ampm == "PM" and hour < 12):
        hour = hour + 12

    # now format the iso string
    estart = "{}T{:02d}:{:02d}".format(date, int(hour), int(mins))
    # and then parse to date for return
    tdate = parser.isoparse (estart)

    return tdate
    # end

# mapping to images
weather_icon_dict = {200:"6", 201:"6", 202:"6", 210:"6", 211:"6", 212 : "6", 
                     221:"6", 230:"6", 231:"6", 232:"6", 
                     300:"7", 301:"7", 302:"8", 310:"7", 311:"8", 312 : "8",
                     313:"8", 314:"8", 321:"8", 
                     500:"7", 501:"7", 502:"8", 503:"8", 504:"8", 511 : "8", 
                     520:"7", 521:"7", 522:"8", 531:"8",
                     600:"V", 601:"V", 602:"W", 611:"X", 612:"X", 613 : "X",
                     615:"V", 616:"V", 620:"V", 621:"W", 622:"W", 
                     701:"M", 711:"M", 721:"M", 731:"M", 741:"M", 751 : "M",
                     761:"M", 762:"M", 771:"M", 781:"M",
                     800:"1", 801:"H", 802:"N", 803:"N", 804:"Y" }

# the fonts
font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
font32 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 32)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font14 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)

font36 = ImageFont.truetype('./epaperws/fonts/arial.ttf', 36)
font28 = ImageFont.truetype('./epaperws/fonts/arial.ttf', 28)
font24 = ImageFont.truetype('./epaperws/fonts/arial.ttf', 24)
font20 = ImageFont.truetype('./epaperws/fonts/arial.ttf', 20)
font16 = ImageFont.truetype('./epaperws/fonts/arial.ttf', 16)
# overwrite the 14 font
font14 = ImageFont.truetype('./epaperws/fonts/arial.ttf', 14)
fontweather = ImageFont.truetype('./epaperws/fonts/meteocons-webfont.ttf', 30)
fontweatherbig = ImageFont.truetype('./epaperws/fonts/meteocons-webfont.ttf', 60)


#
# retrieve the access keys from the environment
owm_key = os.environ.get('OWM_KEY')
met_id = os.environ.get('MET_ID')
met_key = os.environ.get('MET_KEY')

if (owm_key == "" or met_id == "" or met_key == ""):
    print ("Please set OWM_KEY, MET_ID and MET_KEY")
    exit(1)

#
# main()
#
try:
    # initialise the owm library
    owm = pyowm.OWM(owm_key)
    #owm = pyowm.OWM("your_key")

    # prep the logo - used to initialise the image
    #ranelaghLogo()

    logging.info("epd7in5_V2 Demo")

    epd = epd7in5_V2.EPD()

    # currently loops 3 times & sleeps 3
    #while (True):
    for loops in range(1):

        logging.info("init and Clear")
        epd.init()
        # don't clear if not needed
        #epd.Clear()

        # get the weather
        logging.info("Start loop ...")
        obs = owm.weather_at_place('London,GB')
        weather = obs.get_weather()
        temperature = weather.get_temperature(unit='celsius')
        sunrise = weather.get_sunrise_time()
        sunset = weather.get_sunset_time()
        print (obs)

        # load wind on start
        logging.info("loadWind ...")
        loadWind()

        # load tides
        logging.info("loadTides ...")
        prtides = loadTides() # array [][]

        #logging.info("loadPosts ...")
        #jdict = loadPosts() # return list
        #noPosts = len(jdict)

        logging.info("loadEvents ...")
        edict = loadEvents() # return list
        noEvents = len(edict)

        logging.info("getMet ...")
        timeseries = getMet() # return list
        noTimeseries = len(timeseries)

        logging.info("4.read bmp file on window")
        # Note changing width/height changes the orientation
        # 255: clear the frame
        Himage2 = Image.new('1', (epd.width, epd.height), 255)
        # draw is just shorthand to make the code more readable
        draw = ImageDraw.Draw(Himage2)
        draw.text((10, 0), 'Club Wind', font = font36, fill = 0)

        bmp = Image.open("./tmp/daywind.bmp")
        bmp2 = Image.open("./tmp/daywinddir.bmp")
        bmp3 = Image.open(ranelaghlogo + ".bmp")
        # these image are 300 x 180 by default - gap 10 pixels
        Himage2.paste(bmp, (10, 46))
        Himage2.paste(bmp2, (10, 180 + 10 + 46)) # 236
        Himage2.paste(bmp3, (10, 2*180 + 20 + 46)) # 236

        # add date & time - bottom left
        tnow = datetime.datetime.now()
        #imgtext = "Date: " + tnow.strftime('%d %b %Y %H:%M')
        imgtext = tnow.strftime('%d %b %Y %H:%M')
        dw, h = draw.textsize(imgtext, font=font24)
        #draw.text((10, 420), imgtext, font = font24, fill = 0)
        # draw 10 pixels in from the right
        draw.text((800-dw-10, 0), imgtext, font = font24, fill = 0)


        # for now this is just to the right
        Column2 = 320 # the horizontal offset
        draw = ImageDraw.Draw(Himage2)
        draw.text((Column2, 0), 'Club Events', font = font36, fill = 0)
        #draw.text((Column2, 0), 'News', font = font36, fill = 0)

        """
        # list new posts
        for x in range(noPosts):
            id = jdict[x]['id']
            pdate = jdict[x]['date']
            rtitle = jdict[x]['title']
            title = rtitle['rendered']

            # need to use strftime & reverse as python doesn't follow isoformat!
            prdate = parser.isoparse(pdate)

            imgtext = prdate.strftime('%d %b %Y') + " - " + title
            #print (id, " ", pdate, " ", title)
            # add 2 pixels - leading is ????
            draw.text((320, x * 20 + 40), imgtext, font = font14, fill = 0)
        # end while
        """

        mecendpoint = 'https://ranelaghsc.co.uk/wp-json/mecexternal/v1/event/'

        for x in range(noEvents):
            id = edict[x]['id']
            pdate = edict[x]['date']
            rtitle = edict[x]['title']
            title = rtitle['rendered']
            rcontent = edict[x]['content']
            content = rcontent['rendered']
            cleantext = BeautifulSoup(content, "lxml").text

            # for each event get the meta-date - another get
            sglurl = mecendpoint + str(id)
            mecreq = requests.get(sglurl)
            # add error checking!
            # request.status_code == 200

            mecdict = mecreq.json()
            eventid = mecdict['ID']
            etitle = mecdict['post']['post_title']
            estart_date = mecdict['meta']['mec_date']['start']['date']
            estart_hour = mecdict['meta']['mec_date']['start']['hour']
            estart_mins = mecdict['meta']['mec_date']['start']['minutes']
            estart_ampm = mecdict['meta']['mec_date']['start']['ampm']
            eend_date = mecdict['meta']['mec_date']['end']['date']
            eend_hour = mecdict['meta']['mec_date']['end']['hour']
            eend_mins = mecdict['meta']['mec_date']['end']['minutes']
            eend_ampm = mecdict['meta']['mec_date']['end']['ampm']

            # denormalise and parse to python date
            prdate = mectodate(estart_date, int(estart_hour), int(estart_mins), estart_ampm)
            #prdate = parser.isoparse(estart)
            imgtext = prdate.strftime('%d %b %Y %H:%M') + " - " + etitle

            # add 2 pixels - leading is ????
            txt = " > " + cleantext[0:65]
            draw.text((Column2, 2*x* 20 + 40), imgtext, font = font16, fill = 0)
            draw.text((Column2, 2*x* 20 + 41), imgtext, font = font16, fill = 0)
            #draw.text((Column2, 2*x* 20 + 42), imgtext, font = font16, fill = 0)
            draw.text((Column2, (2*x+1) * 20 + 40), txt, font = font16, fill = 0)
            #draw.text((Column2, 2*x* 20 + 40), imgtext, font = font14, fill = 0)
            #draw.text((Column2, (2*x+1) * 20 + 40), txt, font = font14, fill = 0)
        # end while

        # now the weather forecast and observations
        # first row is 236
        draw.text((Column2, 236), "Weather", font = font36, fill = 0)

        # add 100 to vert offset
        draw.text((Column2 + 150, 236 - 25), weather_icon_dict[weather.get_weather_code()], font = fontweatherbig, fill = 0)
        tempstr = str("{0}{1}C".format(int(round(temperature['temp'])), u'\u00b0'))
        draw.text((Column2 + 225, 236 + 12), tempstr, font = font24, fill = 0)


        # forecast at 236 + 36 + 2266 -> 274 and lists the next 6 hours
        tstr =  "Time:"
        twind = "Wind:"
        tgust = "Gust:"
        tdir =  "Dir:"
        ttemp = "Temp:"
        draw.text((Column2, 274 + 0 * 18), tstr, font = font16, fill = 0)
        draw.text((Column2, 274 + 1 * 18), twind, font = font16, fill = 0)
        draw.text((Column2, 274 + 2 * 18), tgust, font = font16, fill = 0)
        draw.text((Column2, 274 + 3 * 18), tdir, font = font16, fill = 0)
        draw.text((Column2, 274 + 4 * 18), ttemp, font = font16, fill = 0)

        for x in range(6):
            ftime = timeseries[x]['time']
            wspeed = timeseries[x]['windSpeed10m']
            gspeed = timeseries[x]['windGustSpeed10m']
            wdir = timeseries[x]['windDirectionFrom10m']
            wtemp = timeseries[x]['screenTemperature']

            idate = parser.isoparse (ftime)
            itime = str("{:%H:%M}".format(idate))
            iwind = str("{:>2d}".format(int(round(wspeed))))
            igust = str("{:>2d}".format(int(round(gspeed))))
            idir = str("{:03d}".format(int(round(wdir))))
            itemp = str("{:>2d}".format(int(round(wtemp))))

            # note the 'width' for column calc
            dw, h = draw.textsize(itime, font=font16)
            ww, h = draw.textsize(iwind, font=font16)
            wg, h = draw.textsize(igust, font=font16)
            wd, h = draw.textsize(idir, font=font16)
            wt, h = draw.textsize(itemp, font=font16)

            draw.text((Column2 + 95 + x*48-dw, 274 + 0*18), itime, font = font16, fill = 0)
            draw.text((Column2 + 95 + x*48-ww, 274 + 1*18), iwind, font = font16, fill = 0)
            draw.text((Column2 + 95 + x*48-wg, 274 + 2*18), igust, font = font16, fill = 0)
            draw.text((Column2 + 95 + x*48-wd, 274 + 3*18), idir, font = font16, fill = 0)
            draw.text((Column2 + 95 + x*48-wt, 274 + 4*18), itemp, font = font16, fill = 0)
            # end of for timeseries

        # and finally the tides!
        tiderow = 236 + 36 + 6 * 18
        draw.text((Column2, tiderow), "Tides (thamestides)", font = font28, fill = 0)
        tidestr = ""
        for row in range (0, 4): # 4 rows
            #for col in range (0, 3): # 5 cols but we only want 0 - 3
                #print (prtides[row][col])
                #if (len(prtides[row][col]) > 0):
                    #tidestr = tidestr + prtides[row][col] + " "
                # end if
            # end for
            # if there are tidal time?, if so then process
            if (len(prtides[row][1]) > 0):
                tidestr = tidestr + prtides[row][0] + ": " \
                        + prtides[row][1] + " " + prtides[row][2] + "m, "
                #tidestr = tidestr + ", "
        # end for
        draw.text((Column2, tiderow + 32), tidestr, font = font14, fill = 0)


        # display and then sleep
        epd.display(epd.getbuffer(Himage2))
        time.sleep(5)
        #loops = loops + 1

        # should put the display to sleep & then delay 5 mins -> 300 seconds
        #logging.info("sleeping ...")
        #epd.sleep()
        #time.sleep(300)

        #time.sleep(180) # minimum refresh interval

    # end processing loop

    # clear display
    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    print ('traceback.format_exc():\n%s', traceback.format_exc())
    logging.info(e)
    epd7in5_V2.epdconfig.module_exit()
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()

# end file
