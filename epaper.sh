#

# set environment
cd ~pi/Epaper
. ./epaper.env

# run the display in background
python3 display.py > display.log 2>&1 &
# echo the pid
echo "PID > " $!

exit 0
