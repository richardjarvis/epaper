#
# code to parse the tidal time from thametides.org
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

def removeNonAscii(s): return "".join(i for i in s if (ord(i)<128 and ord(i)>31))

page = requests.get('https://thamestides.org.uk/dailytides2.php?statcode=PUT&startdate=0')
if (page.status_code == 200):
    print ("Success")

tree = html.fromstring(page.content)

#print (tree)
#//*[@id="content"]/table/tbody/tr[1]
tab = tree.xpath('//*[@id="content"]/table')
# table header
tab1 = tree.xpath('//table[@class="first"]//tr[1]//text()')
#row4 = tree.xpath('//*[@id="content"]/table/tbody/tr[7]/text()')


#cell41  = tree.xpath('//table[@class="first"]//tr[4]//td[1]//text()')
#cell42  = tree.xpath('//table[@class="first"]//tr[4]//td[2]//text()')
#cell43  = tree.xpath('//table[@class="first"]//tr[4]//td[3]//text()')
#cell44  = tree.xpath('//table[@class="first"]//tr[4]//td[4]//text()')
#cell45  = tree.xpath('//table[@class="first"]//tr[4]//td[5]//text()')
#cell51  = tree.xpath('//table[@class="first"]//tr[5]//td[1]//text()')
#cell52  = tree.xpath('//table[@class="first"]//tr[5]//td[2]//text()')
#cell53  = tree.xpath('//table[@class="first"]//tr[5]//td[3]//text()')
#cell54  = tree.xpath('//table[@class="first"]//tr[5]//td[4]//text()')
#cell55  = tree.xpath('//table[@class="first"]//tr[5]//td[5]//text()')
#cell61  = tree.xpath('//table[@class="first"]//tr[6]//td[1]//text()')
#cell62  = tree.xpath('//table[@class="first"]//tr[6]//td[2]//text()')
#cell63  = tree.xpath('//table[@class="first"]//tr[6]//td[3]//text()')
#cell64  = tree.xpath('//table[@class="first"]//tr[6]//td[4]//text()')
#cell65  = tree.xpath('//table[@class="first"]//tr[6]//td[5]//text()')
#cell71  = tree.xpath('//table[@class="first"]//tr[7]//td[1]//text()')
#cell72  = tree.xpath('//table[@class="first"]//tr[7]//td[2]//text()')
#cell73  = tree.xpath('//table[@class="first"]//tr[7]//td[3]//text()')
#cell74  = tree.xpath('//table[@class="first"]//tr[7]//td[4]//text()')
#cell75  = tree.xpath('//table[@class="first"]//tr[7]//td[5]//text()')

#extract the items to an array

# construct the two dimensional list
items = []

print (len(items))
if (len(items) == 0): # then initialise
    for j in range(4, 4 + 5): # should be 4 - 8
        column = []
        for i in range(1,6):
            column.append("")
        items.append(column)
# now initialised
print (len(items))

# now parse the table into the array - note doesn't error
for row in range (4, 4 + 5):
    for col in range(1,6):
        # returns list
        item = tree.xpath('//table[@class="first"]//tr['
                    + str(row) + ']//td[' + str(col) + ']//text()')
        if (len(item) > 0):
            #items[row-4][col-1] = item[0]
            items[row-4][col-1] = removeNonAscii(item[0])
        else:
            items[row-4][col-1] = ""
        #print ("items ", str(row), str(col), items[row-4][col-1])
    # for
# for

#//*[@id="content"]/table/tbody/tr[5]/td[2]/b
#//*[@id="content"]/table/tbody/tr[5]/td[3]/b

#print (tab1)
print (tab1[0])
#print (cell41, cell42, cell43, cell44, cell45)
#print (cell51, cell52, cell53, cell54, cell55)
#print (cell61, cell62, cell63, cell64, cell65)
#print (cell71, cell72, cell73, cell74, cell75)

tstr = "" # a string
for row in range(5):
    print (str(items[row][0]), len(items[row][0]))
    for col in range(5):
        print (items[row][col], "!", end='')
        #print (len(items[row][0]))
    print ()

# end of file
