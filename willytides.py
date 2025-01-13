from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timezone, timedelta

# New Tidal Data source from willyweather.co.uk

willy_tides = None

def loadWillyTides():
    global willy_tides
    url = 'https://tides.willyweather.co.uk/se/greater-london/river-thames----putney-bridge.html'
    html = requests.get(url).text
    # return html
    soup = BeautifulSoup(html, 'lxml')
    forecast = soup.find('section', class_='forecast')
    willy_tides = None if forecast is None else forecast.find('ul')


def getWillyTides(dt, reset=False):
    if reset or willy_tides is None:
        loadWillyTides()
    if willy_tides is None:
        return None
    for days_tide in willy_tides:
        day = days_tide.find('time').attrs.get('datetime')
        if day == dt:
            tide_list = days_tide.find('ul')
            tides = []
            for tide in tide_list:
                try:
                    ttype = 'High' if 'point-high' in tide.attrs.get('class') else 'Low'
                    ttime12, ampm = tide.find('h3').text.split(' ')     # comes in format '5:42 am', etc
                    hr, mins = [int(x) for x in ttime12.split(':')]
                    if ampm == 'pm' and hr < 12:
                        hr += 12
                    elif ampm == 'am' and hr == 12:
                        hr = 0
                    ttime = f'{hr:02d}:{mins:02d}'
                    theight = tide.find('span').text[:-1]               # comes in format 4.35m
                    tide = {'type': ttype, 'time': ttime, 'height': theight}
                    tides += [tide]
                except Exception as e:
                    pass
            return tides
    return []
    
if __name__ == '__main__':
    today = date.today()
    for days in range(0, 8):
        dt = (today + timedelta(days=days)).isoformat()
        tides = getWillyTides(dt)
        print(dt)
        for tide in tides or []:
            print(tide)
