#

# set environment
cd /home/pi/Epaper
. ./epaper.env

# run the display in background
python3 ./display.py > display.log 2>&1 &
# echo the pid & if tty
if [ -t 1 ]; then
	echo "PID > " $!
fi

exit 0
