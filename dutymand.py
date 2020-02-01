'''
    dutymand.py - scrapes schedules from dutyman.biz for a roster.biz

'''
#import re
#import logging
#import xml.etree.ElementTree as ET

import requests
from lxml import html
#from suds.client import Client
import datetime
from dateutil import parser


#DUTYMAN_API_ENDPOINT = "http://www.dutyman.biz/api/dutyman.asmx"
#DUTYMAN_API_NS = "http://www.dutyman.biz/api/"
#DUTYMAN_API_TIMEOUT = 10


class URLParser:
    ''' Handles downloading and parsing HTML '''

    def __init__(self, url):
        self.url = url
        self.tree = self.download_page(url)
        if self.tree is None:
            raise Exception(f"Could not download the page ({url})")

    def download_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        tree = html.fromstring(response.content)
        assert tree is not None
        if response.status_code != 200:
            return None
        return tree


class DutyMan:
    '''
    Handles retrieve duties for the rosterid - dbpassword not needed
    '''

    def __init__(self, roster_id=None, db_password=None, use_wsdl=True, debug=False):
        ''' initialize the DutyMan Python API

        Arguments:
            roster_id {str} -- user ID
            db_password {str} -- password

        Keyword Arguments:
            use_wsdl {bool} -- whether to use WSDL API description scheme file provided by server or pure python calls (default: {True})
        '''

        self.roster_id = roster_id
        self.db_password = db_password
        self.use_wsdl = use_wsdl
    # end __init__


    def getDuties(self, roster_id, max_duties=9999, max_events=9999):
        ''' Get duties

        Arguments:
            roster_id {str} -- Roster ID (Member ID)

        Keyword Arguments:
            max_duties {number} -- max number of duties to return (default: {9999})
            max_events {number} -- max number of events to return (default: {9999})

        Returns:
            array of dictionaries -- duties
        '''
        duties = []
        parsered = URLParser(f'https://dutyman.biz/dmembed.aspx?id=R0001532&mode=2&maxrows={max_duties}')
        rows = parsered.tree.xpath('//tr')
        n_events = 0
        for row in rows:
            xdate = row.xpath('td[1]/span[1]/text()')
            if len(xdate) > 0:
                date = xdate[0].strip()
            xevent = row.xpath('td[2]/span[1]/text()')
            if len(xevent) > 0:
                event = xevent[0].strip()
                n_events += 1
                if n_events > max_events:
                    break
            xduty = row.xpath('td[3]/span[1]/text()')
            if len(xduty) > 0:
                duty_name = xduty[0].strip()
            xperson = row.xpath('td[4]/span[1]/text()')
            if len(xperson) > 0:

                # convert date to iso "yyyy-mm-dd"
                # format "Sun, 23 Feb", "Today", "Tomorrow"
                tnow = datetime.datetime.now()
                dateobj = tnow
                #edate = tnow.date()
                if (date == "Today"):
                    dateobj = tnow
                    #edate = dateobj.date()
                elif (date == "Tomorrow"):
                    dateojb = tnow + dateutil.relativedelta.relativedelta(days=1)
                    #edate = dateobj.date()
                else:
                    dateobj = parser.parse(date)
                    #edate = dateobj.date()

                edate = dateobj.date()


                person = xperson[0].strip()
                duty = {'date': str(edate), 'event': event, 'duty': duty_name, 'person': person}
                duties.append(duty)

        return duties

    def getEvents(self, roster_id, max_duties=9999, max_events=9999):
        ''' Get events

        Arguments:
            roster_id {str} -- Roster ID (Member ID)

        Keyword Arguments:
            max_duties {number} -- max number of duties to return (default: {9999})
            max_events {number} -- max number of events to return (default: {9999})

        Returns:
            array of dictionaries -- events
        '''
        duties = self.getDuties(roster_id, max_duties, max_events)
        events = set([duty['date'] + '|' + duty['event'] for duty in duties])
        events = [event.split('|') for event in events]
        events = [{'date': event[0], 'event': event[1]} for event in events]
        return events
