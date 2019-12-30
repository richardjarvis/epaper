#
# code for pyown
#

import os
import sys
import time

#sys.path.append("/usr/local/lib/python3.7/dist-packages")

# retrieve the access keys from the environment
owm_key = os.environ.get('OWM_KEY')

if (owm_key == ""):
    print ("Please set OWM_KEY")
    exit(1)
#

import pyowm

# initialise the library
owm = pyowm.OWM(owm_key)

location_code = 2643741


# mapping to images
weather_icon_dict = {200 : "6", 201 : "6", 202 : "6", 210 : "6", 211 : "6", 212 : "6", 
                     221 : "6", 230 : "6" , 231 : "6", 232 : "6", 

                     300 : "7", 301 : "7", 302 : "8", 310 : "7", 311 : "8", 312 : "8",
                     313 : "8", 314 : "8", 321 : "8", 
 
                     500 : "7", 501 : "7", 502 : "8", 503 : "8", 504 : "8", 511 : "8", 
                     520 : "7", 521 : "7", 522 : "8", 531 : "8",

                     600 : "V", 601 : "V", 602 : "W", 611 : "X", 612 : "X", 613 : "X",
                     615 : "V", 616 : "V", 620 : "V", 621 : "W", 622 : "W", 

                     701 : "M", 711 : "M", 721 : "M", 731 : "M", 741 : "M", 751 : "M",
                     761 : "M", 762 : "M", 771 : "M", 781 : "M", 

                     800 : "1", 

                     801 : "H", 802 : "N", 803 : "N", 804 : "Y"
}



# get the weather and decode


        # Get Weather data from OWM
#obs = owm.weather_at_id(location_code)
obs = owm.weather_at_place('London,GB')

print (obs)

location = obs.get_location().get_name()
weather = obs.get_weather()
reftime = weather.get_reference_time()
description = weather.get_detailed_status()
temperature = weather.get_temperature(unit='celsius')
humidity = weather.get_humidity()
pressure = weather.get_pressure()
clouds = weather.get_clouds()
wind = weather.get_wind()
rain = weather.get_rain()
sunrise = weather.get_sunrise_time()
sunset = weather.get_sunset_time()

print("location: " + location)
print("weather: " + str(weather))
print("description: " + description)
print("temperature: " + str(temperature))
print("humidity: " + str(humidity))
print("pressure: " + str(pressure))
print("clouds: " + str(clouds))
print("wind: " + str(wind))
print("rain: " + str(rain))
print("sunrise: " + time.strftime( '%H:%M', time.localtime(sunrise)))
print("sunset: " + time.strftime( '%H:%M', time.localtime(sunset)))

exit 
