#
# demo code for the wordpress mec rest api
# this now works with the shortcode apis
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

import requests
import json
import datetime
import dateutil.relativedelta
from bs4 import BeautifulSoup


# The main access url for the wordpress site
siteurl = "https://ranelaghsc.co.uk/"
# for list events
#eventurl = siteurl + "wp-json/wp/v2/mec_events"
eventurl = "https://ranelaghsc.co.uk/wp-json/wp/v2/mec-events"
# request single event
mecurl = siteurl + "wp-json/mecexternal/v1/event/"

# note the current date & calc the date for the last month and the convert
tnow = datetime.datetime.now()
ptime = tnow - dateutil.relativedelta.relativedelta(months=1)
tquery = ptime.isoformat()


# request the last 3 events
reqstr = eventurl + "?per_page=15&order=desc"

# this is based on the events calendar view
# it returns the next 6 events
reqstr = "https://www.ranelaghsc.co.uk/wp-json/mecexternal/v1/calendar/922"

print ("Querying: ", reqstr)
req = requests.get(reqstr)

if req.status_code == 200:
    print('Success!')
elif req.status_code == 404:
    print('Not Found.')
    exit (1)

# extract the dict[
pdict = req.json()

print ("No of events ", type(pdict), len(pdict))

# iterate over the events and extract each in turn
#for x in pdict:
    #print ("Element: ", x)

#print ("content_json: ", type (pdict["content_json"]), pdict["content_json"])
#print ("html: ", pdict["content_html"])

jdict = pdict["content_json"] # this is actually the data

print ("len of data: ", len(jdict))

events = ["", "", ""]
cnt = 0
for x in jdict: # this is the top level
    #print ("content_json elements: ", x)
    #print (type(x), len(x))

    #print (type(tdict[x]))
    #print (tdict[x])

    for y in jdict[x]: # this at the date or individual level
        #print (type(y), len(y))
        #for v in y:
        #    print (v)

        #print(type(y["data"])) # data
        #print(y["data"])


        #for z in y["data"]:
            #print (z)
            #print (y["data"][z])

        #for r in y["data"]["meta"]:
            #print (r)

        # which has id, data and date
        stitle = y["data"]["title"]
        scontent = y["data"]["content"]
        sdate = y["data"]["meta"]["mec_start_date"]
        shour = y["data"]["meta"]["mec_start_time_hour"]
        smins = y["data"]["meta"]["mec_start_time_minutes"]
        sampm = y["data"]["meta"]["mec_start_time_ampm"]

        print (stitle, scontent, sdate, shour, smins, sampm)

        if (cnt < 3): # then note the dict entry
            events[cnt] = y["data"]
            cnt = cnt + 1

# end of dict
for x in range (cnt):
    print (x, BeautifulSoup(events[x]["title"], features="lxml").text)


# end of file
