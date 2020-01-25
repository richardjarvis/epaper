#
# code to parse the EA guage readings for flow
#
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

from lxml import html
import requests

"""
    cumecs (m3/sec)     flow description
    0 to 20                    Low
    20 to 150                Average (I say "within normal range")
    150 to 300              Strong
    More than 300         Very Strong

    Negative  Usually when a very high tide has gone beyond Teddington
                             and is still going as it passes Kingston!
"""

# the url or EA Kingston guage - looks to be update every 30 mins
# so mod 6
eauk = 'https://environment.data.gov.uk/flood-monitoring/id/stations/3400TH/readings?latest'
page = requests.get(eauk)
if (page.status_code == 200):
    print ("Success")

tree = page.json()
print (len(tree))
#print (tree)
for x in tree:
    print (x)
#print (tree[0])
#print (tree[1])
#print (tree["items"])
for x in tree["items"]:
    #print (x)
    print (x['@id'])
    print (x['dateTime'])
    print (x['value'])

level = tree["items"][0]
flow = tree["items"][1]

flowval = int(flow["value"])

if (flowval > 0 and flowval <= 20):
    flowtext = "Low"
elif (flowval > 20 and flowval <= 150):
    flowtext = "Average"
elif (flowval > 150 and flowval <= 300):
    flowtext = "Strong"
else:
    flowtext = "Very strong"
    
flowtext = flowtext + " fluvial flows"

print (level["value"], flow["value"], flowtext)

#print (tree["items"]["@id"])


# end of file
