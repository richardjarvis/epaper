#

# set environment
cd /home/pi/Epaper
. ./epaper.env

# run the display in background
source /home/pi/.venv/epaper/bin/activate
python3 ./races.py > races.log 2>&1 &
# echo the pid & if tty

exit 0
