import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='')
curr = conn.cursor()
curr.execute('USE times_square')

curr.execute('SELECT DISTINCT Sub_subindustry FROM sub_subindustry')
List=curr.fetchall()
SSIstring = ""

for item in List:
    for x in item:
        SSIstring+=str(x)+', '

    (SSIstring)

RestaurantType = raw_input("Out of the following restaurant types, which is most similar to the restaurant you are thinking of opening? ("+SSIstring+") ")
proposed_location = raw_input("What is the address of the location where you are hoping to open your Times Square restaurant? (eg. 120 W 42nd St) ")

curr.execute("SELECT idSub_subindustry FROM sub_subindustry WHERE Sub_subindustry = %s", RestaurantType)
id_type = curr.fetchone()
food_type_id = id_type[0]


curr.execute("SELECT idRestaurant FROM intermediate_rest_subsub WHERE SubSubIndustry = %s", food_type_id)
ids_restaurants = curr.fetchall()
ids_restaurant_string = [x[0] for x in ids_restaurants]
restaurants = {}

for x in ids_restaurant_string:
    curr.execute("SELECT idAddress FROM intermediate_rest_location WHERE idRestaurant = %s", (x))
    idAddress = curr.fetchone()
    curr.execute("SELECT Location FROM address WHERE idAddress = %s", (idAddress[0]))
    address = curr.fetchone()
    address_string = address[0] + ""
    restaurants[x] = address_string



from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import great_circle

restaurant_distances = []

for item in ids_restaurant_string:

    temp = restaurants[item] + ""
    specific_location = temp + " nyc"

    if "Seventh" in specific_location:
        specific_location = specific_location.replace('Seventh', '7th')
    elif "Eight" in specific_location:
        specific_location = specific_location.replace('Eighth', '8th')

    try:
        specific_location_latitude = Nominatim().geocode(specific_location, timeout= 1000).latitude
        specific_location_longitude = Nominatim().geocode(specific_location, timeout= 1000).longitude
    except AttributeError:
        pass

    try:
        proposed_location = proposed_location + " nyc"
        proposed_location_latitude = Nominatim().geocode(proposed_location, timeout= 1000).latitude
        proposed_location_longitude = Nominatim().geocode(proposed_location, timeout= 1000).longitude
    except AttributeError:
        pass

    distance = great_circle((specific_location_latitude, specific_location_longitude), (proposed_location_latitude, proposed_location_longitude)).miles
    restaurant_distances.append((item, distance))



from operator import itemgetter

##restaurant_distances = [(21, 0.09525602506604319), (31, 6.236655991128893), (58, 0.13460015347420856), (61, 0.47560032291099363), (173, 0.47108689743599536), (216, 0.3999835419921544), (255, 0.3460904392225489), (285, 0.41790544775286365), (303, 0.09673793362837162)]

restaurant_distances_sorted = sorted(restaurant_distances, key=itemgetter(1))

temp_distances = []
temp_names = []

count = 0
for x in restaurant_distances_sorted:
    if count < 5:
        curr.execute("SELECT CompanyName FROM restaurant WHERE idRestaurant = %s", x[0])
        rest_name = curr.fetchone()
        print (rest_name[0] + " at a distance of "+ str(x[1]))
        temp_distances.append(x[1])
        temp_names.append(rest_name[0])
        count = count + 1


import numpy as np
import matplotlib.pyplot as py

fig = py.figure()
ax = fig.add_subplot(111)

N = 5
closest_distances = [temp_distances[0],temp_distances[1],temp_distances[2],temp_distances[3],temp_distances[4]]

ind = np.arange(N)
width = 0.35

ax.bar(ind, closest_distances, width,
                color='black')

# axes and labels
ax.set_xlim(-width,len(ind)+width)
ax.set_ylim(0,temp_distances[4] + 0.1)
ax.set_ylabel('Distance from Proposed Location (miles)')
ax.set_title('Closest Restaurants')
xTickMarks = [temp_names[0],temp_names[1],temp_names[2],temp_names[3],temp_names[4]]
ax.set_xticks(ind+width)
xtickNames = ax.set_xticklabels(xTickMarks)
py.setp(xtickNames, rotation=45, fontsize=10)

py.show()


