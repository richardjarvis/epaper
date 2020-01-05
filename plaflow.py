#
# code to parse the pla status page for the flow
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

