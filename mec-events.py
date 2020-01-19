#
# demo code for the wordpress mec rest api
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

print ("Querying: ", reqstr)
req = requests.get(reqstr)

if req.status_code == 200:
    print('Success!')
elif req.status_code == 404:
    print('Not Found.')
    exit (1)

# extract the dict[
pdict = req.json()

print ("No of events ", len(req.json()))

# iterate over the events and extract each in turn
for x in range(len(pdict)):
    id = pdict[x]['id']
    pdate = pdict[x]['date']
    rtitle = pdict[x]['title']
    title = rtitle['rendered']

    print (id, " ", pdate, " ", title)

    # get the single MEC event record
    print ("MEC query ", mecurl + str(id))
    mecreq = requests.get(mecurl + str(id))
    if mecreq.status_code == 200:
        print('Success!')
    else:
        print('Not Found.', mecreq.status_code)
        exit (1)

    mecdict = mecreq.json()

    print ("> ", mecdict['ID'], " ",
        mecdict['post']['post_title'], " ",
        mecdict['meta']['mec_date']['start']['date'], " ",
        mecdict['meta']['mec_date']['start']['hour'], " ",
        mecdict['meta']['mec_date']['start']['minutes'], " ",
        mecdict['meta']['mec_date']['start']['ampm']
        )

    x = x+1
    # end of while

# end of file
