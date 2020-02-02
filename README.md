# Epaper
This is a simple app that integrates a number of feeds and displays them on Waveshae 7.5 EPD (electronic paper display). For each of the data sources there is file to support exporing the api so that changes can be evaluated outside of the main display code. This makes development more straight forward and faster. The display is driven by a raspberry pi zero w and refreshes very 5 mins which reflects the weather update frequency.

The data sources are:
- The wind data comes from the club's weather station (Davis Vantage Pro and WeeWX)
- Events come from the clubs website which is wordpress based
- The weather observation are via the open weather network
- The forecast is from the met office via their datahub interface
- River flow comes from the EA as it is updated more regularly than the PLA
- and the tide info is scrapped from thametimes.org.uk

Note: any keys are injected by environment variables so you'll need to create your own epaper.env file and source this before running the code.

Also include here is the races program which sends out a summary email of upcoming races to the list 'racing@ranelaghsc.co.uk . This draws data from a number of sources:

- The race events come from the Club's wordpress site
- The duty scedule is scrapped from the club roster on dutyman.biz
- The tidal data from Thamestides.org
- And the weather from the metoffice 3 hourly 7 day forecast for the club



