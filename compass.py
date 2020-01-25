#
# test the wind direction calc
#

# compass direction for the wind direction summary
compass = ["N","NNE","NE",
            "ENE","E","ESE",
            "SE","SSE","S",
            "SSW","SW","WSW","W",
            "WNW","NW","NNW","N"]

def windDir(dir):
    global compass

    direction = ""

    direction = compass[int(round(dir/22.5, 0))]

    return direction

# end windDir


# main

dir = 1
while (dir < 360):
    print (dir, " -> ", windDir(dir), " ", dir/22.5)
    dir = dir + 14

