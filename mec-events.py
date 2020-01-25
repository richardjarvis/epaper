#
# demo code for the wordpress mec rest api
# this now works with the shortcode apis
#
#

import requests
import json
import datetime
import dateutil.relativedelta


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
    print (x, events[x]["title"])


# end of file
