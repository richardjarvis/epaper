#
#
#


#test sample met office code - need to convert to request()

import requests
import geojson
import http.client

meturl = "https://api-metoffice.apiconnect.ibmcloud.com"
conn = http.client.HTTPSConnection("api-metoffice.apiconnect.ibmcloud.com")

headers = {
    'x-ibm-client-id': "4fb7d86f-aeb4-40d7-b78d-f3ed2dd81a2b",
    'x-ibm-client-secret': "Y8xW2uN8vM0dQ0sD0uQ1xB5aK3sC6vY5eK1tA5yQ6lN5hY1bI8",
    'accept': "application/json"
    }

metreq = "/metoffice/production/v0/forecasts/point/hourly?excludeParameterMetadata=false&includeLocationName=false&latitude=51.469&longitude=-0.2199"

conn.request("GET", "/metoffice/production/v0/forecasts/point/hourly?excludeParameterMetadata=false&includeLocationName=false&latitude=51.469&longitude=-0.2199", headers=headers)

res = conn.getresponse()
data = res.read()

#print(data.decode("utf-8"))


req = requests.get(meturl + metreq, headers=headers)
print (req.status_code)
#print (req.json())

#rgeo = geojson(req.text)
rdict = req.json()

# this print 3 as there are type, features and parameters
print (len(rdict))

#for x in range(len(rdict)):
#    print (rdict[x][0])

x = 0
for feature in rdict['features']:
    print ("Loop: ", x)
    print (feature['type'])
    print (feature['geometry']['type'])
    print (feature['geometry']['coordinates'])
    print (feature['properties']['requestPointDistance'])
    print (feature['properties']['modelRunDate'])
    timeseries = feature['properties']['timeSeries']
    #print (feature['properties']['location']['name'])
    x = x + 1


print (len(timeseries))
"""
# list next 6 hours
for tentry in timeseries:
    print (tentry['time'],
            " ", tentry['windSpeed10m'],
            " ", tentry['windGustSpeed10m'],
            " ", tentry['windDirectionFrom10m'],
            " ", tentry['screenTemperature'])
"""

# list next 6 hours
for x in range(6):
    print (timeseries[x]['time'],
            " ", timeseries[x]['windSpeed10m'],
            " ", timeseries[x]['windGustSpeed10m'],
            " ", timeseries[x]['windDirectionFrom10m'],
            " ", timeseries[x]['screenTemperature'])

type = rdict['type']

type = rdict['type']
print (type)
fdict = rdict['features']
#type = fdict['type']
#print (type)
#location = rdict['features']['properties']['location']['name']
#print (location)

# end
