#
# file to downlaod the wind data and convert the pngs
#

import requests
from PIL import Image

windurl = "https://wind.ranelaghsc.co.uk/daywind.png"
winddirurl = "https://wind.ranelaghsc.co.uk/daywinddir.png"
#url = "https://wind.ranelaghsc.co.uk/daywind.png"
#url = 'http://google.com/favicon.ico'

print ("Download")
r = requests.get(windurl, allow_redirects=True)
open('daywind-copy.png', 'wb').write(r.content)

r2 = requests.get(winddirurl, allow_redirects=True)
open('daywinddir-copy.png', 'wb').write(r2.content)

# we'll use the downloaded png and see if we can get a 1 bit bmp
print ("Converting to 1-bit dithered")
file_in = "daywind"
#file_in = "daywind-copy.png"
img = Image.open(file_in + "-copy.png")
img2 = img.convert("1")
#img2 = img.convert("1", dither=Image.NONE)
#file_out = "daywind-copy.bmp"
img2.save(file_in + "-copy.bmp")

file_in = "daywinddir"
img = Image.open(file_in + "-copy.png")
img2 = img.convert("1")
img2.save(file_in + "-copy.bmp")


#img = Image.open("daywinddir-copy.png")
#r, g, b, a = img.split()
#im1 = img.split()
#img2 = Image.merge("RGB", (im1[0], im1[1], im1[2]))
#img2.save("daywinddir-copy.bmp")


