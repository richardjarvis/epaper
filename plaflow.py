#
# code to parse the pla status page for the flow
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


page = requests.get('http://www.pla.co.uk/templates/widgets/trafficWidget.cfm')
#page = requests.get('https://thamestides.org.uk/dailytides2.php?statcode=PUT&startdate=0')
if (page.status_code == 200):
    print ("Success")

tree = html.fromstring(page.content)

#print (tree)
#//*[@id="content"]/table/tbody/tr[1]
tab = tree.xpath('//*[@id="content"]/table')
# table header
tab1 = tree.xpath('//table[@class="first"]//tr[1]//text()')
#row4 = tree.xpath('//*[@id="content"]/table/tbody/tr[7]/text()')

# /html/body/table/tbody/tr[48]/td[2]/text()

#text1 = tree.xpath('//html//body//table//tbody//tr[48]//text()')
#text1 = tree.xpath('//html//body//table//tbody//tr[48]//td[2]//text()')
text1 = tree.xpath('//span[@class="warningTitle"]//text()')

print (type(text1))
print (text1[0])

print (" > ", text1[0], " ", text1)

# end of file
