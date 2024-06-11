#

# set environment
cd /home/pi/Epaper
. ./epaper.env

# run the display in background
python3 ./races2.py > races2.log 2>&1 &
# echo the pid & if tty

exit 0
