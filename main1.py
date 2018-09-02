import pandas as pd
import json
import sys
import pdb
from datetime import datetime as dt
import datetime
import urllib.request


# from geopy.distance import great_circle
# from shapely.geometry import MultiPoint
# from datetime import datetime as dt
from math import radians, cos, sin, asin, sqrt, atan2

# define the number of kilometers in one radian
kms_per_radian = 6371.0088

radius = 0.1
eps_rad = radius / kms_per_radian

key = "AIzaSyB9kjlneNrld9gqGJb60ncVDOUuBdYa37s" 
key2 = "AIzaSyDxxslZEt-75zj2mLR4oXzip4BazkPFHVE"


# https://roads.googleapis.com/v1/snapToRoads?path=-35.27801,149.12958&interpolate=true&key=AIzaSyDxxslZEt-75zj2mLR4oXzip4BazkPFHVE

# https://roads.googleapis.com/v1/snapToRoads?path=-35.27801,149.12958&interpolate=false&key=AIzaSyDxxslZEt-75zj2mLR4oXzip4BazkPFHVE

# https://roads.googleapis.com/v1/snapToRoads?path=44.4173183,26.0499215&interpolate=false&key=AIzaSyDxxslZEt-75zj2mLR4oXzip4BazkPFHVE

# https://roads.googleapis.com/v1/snapToRoads?path=44.4173183,26.0499215&interpolate=false&key=AIzaSyDxxslZEt-75zj2mLR4oXzip4BazkPFHVE

def distance(lat1, lon1, lat2, lon2):
    radius = 6371.0088 # km in one radian

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c
    
    return d

def point_index_in_cluster(lat, lon, df_clustered):
    index = -1

    for i, cluster in enumerate(df_clustered.itertuples()):
        if distance(lat, lon, cluster[1], cluster[2]) < radius:
            return i

    return index

def get_street_name_offline(lat, lon):
    if(lat == 44.4379451 and lon == 26.0596271):
       return "Șoseaua Grozăvești"
    if(lat == 44.4121317 and lon == 26.017119):
       return "Aleea Valea Salciei"
    if(lat == 44.4162349 and lon == 26.0517954):
       return "Bulevardul Ghencea"
    
def get_street_name_online(lat, lon):
    google_url = "https://roads.googleapis.com/v1/snapToRoads?path="
    google_url += str(lat)
    google_url += ","
    google_url += str(lon)
    google_url += "&interpolate=false&key=" + key2
    
    bytes_answer = urllib.request.urlopen(google_url).read()
    text_answer = bytes_answer.decode("utf8")
    google_answer = json.JSONDecoder().decode(text_answer)
    
    print("google answered...")
    
    snapped_lat = google_answer["snappedPoints"][0]["location"]["latitude"]
    snapped_lon = google_answer["snappedPoints"][0]["location"]["longitude"]
    
    snapped_lat = str(snapped_lat)
    snapped_lon = str(snapped_lon)
    
    
    bytes_data = urllib.request.urlopen("https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?prox="+snapped_lat+"%2C"+snapped_lon+"%2C250&mode=retrieveAddresses&maxresults=1&gen=9&app_id=WWBAntTsRvOS0fscgPXJ&app_code=4NuAvXOIiG1gaP_vFTgu5Q").read()

    text_data = bytes_data.decode("utf8")
    here_answer = json.JSONDecoder().decode(text_data)
    
    
    
    address = here_answer["Response"]["View"][0]["Result"][0]["Location"]["Address"]
    street = "notReturnedByHere"
    if ("Street" in address):
        street = address["Street"]
    
    print("here answered...{}".format(street))
    return street

def time_difference(date_time1, date_time2):
    d1 = datetime.datetime.strptime(date_time1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(date_time2, '%Y-%m-%d %H:%M:%S')
    return (d2 - d1).total_seconds() / 60

def get_street_name(lat, lon): 
    return get_street_name_online(lat, lon)
#    return get_street_name_offline(lat, lon)
        

if (len(sys.argv) != 2):
    print("example of usage: python main.py examples/example1.json")
    sys.exit(1)

examplefile = sys.argv[1]


df_test = pd.read_csv(examplefile)

with open('transition_mat_with_streets.json', 'r') as f:
    transition_mat = json.load(f)
# import pdb; pdb.set_trace()
with open('transition_list.json', 'r') as f:
    history_transition_list = json.load(f)
   
with open('sp_trans_list.json', 'r') as f:
    history_sp_trans_list = json.load(f)
    
with open('interest_points.json', 'r') as f:
    interest_points = json.load(f)
    
with open('max_times.json', 'r') as f:
    max_times = json.load(f)
    
with open('schedule.json', 'r') as f:
    schedule = json.load(f)
    
with open('routes_max_times.json', 'r') as f:
    routes_max_times = json.load(f)

df_clustered = pd.read_csv('user-location-clustered.csv') 
last = -1
test_transition_list = []
test_sp_trans_list = []
street_name = []
# start reading the example file list
for i in range(df_test.shape[0]):
    p_in_cl = point_index_in_cluster(df_test.iloc[i]['lat'], df_test.iloc[i]['lon'], df_clustered)
    if p_in_cl > -1:
        if not last == p_in_cl:
            test_transition_list.append(p_in_cl)
            test_sp_trans_list.append([df_test.iloc[i]['time'], df_test.iloc[i]['time']])
            last = p_in_cl
        else:
            test_sp_trans_list[-1][1] = df_test.iloc[i]['time']
    else:
        current_street = get_street_name(df_test.iloc[i]['lat'], df_test.iloc[i]['lon'])
        if current_street not in street_name and current_street != 'notReturnedByHere':
            street_name.append(current_street)
             
print(test_transition_list)
print(test_sp_trans_list)
print(street_name)
    
# # df_gps = pd.read_csv('user_location_with_snap_points_and_streets.csv')  

 

day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

key = "AIzaSyB9kjlneNrld9gqGJb60ncVDOUuBdYa37s" 

json_decode = json.JSONDecoder()

outside_cluster = test_sp_trans_list[0][1]
number_of_clusters = len(test_sp_trans_list)

if len(test_sp_trans_list) >1: 
    end_point = test_transition_list[-1]
else:
    # outside_cluster = 0
    end_point = -1
     
start_point = test_transition_list[0]

if(number_of_clusters == 1):
    time_in_cluster = time_difference(test_sp_trans_list[0][0], test_sp_trans_list[0][1])
    if(time_in_cluster > max_times[start_point]):
        print("{} minutes spent in current point {} are more than the history max ({} minutes) for this point. Sending an alert.".format(time_in_cluster, start_point, max_times[start_point]))
        sys.exit(0)
    else:
        print("{} minutes spent in current point {} are less than the history max ({} minutes) for this point. This looks ok.".format(time_in_cluster, start_point, max_times[start_point]))


if(number_of_clusters > 1):
    if(schedule[end_point] == "any_time_is_ok"):
        print("At this interest point {}, the user can be at any time during the day. This looks ok.".format(end_point))
    else:
        current_time = datetime.datetime.strptime(test_sp_trans_list[-1][0], '%Y-%m-%d %H:%M:%S')
        weekday = current_time.weekday()
        hour = current_time.hour
        
        if(schedule[end_point][weekday][hour] == "never"):
            print("Never before this interest point {} has been visited on a {} and between {} and {}. Sending an alert.".format(end_point, day_names[weekday], hour, hour + 1))
            sys.exit(0)
        else:
            print("This interest point {} has been visited before on a {} and and between {} and {}. This looks ok.".format(end_point, day_names[weekday], hour, hour + 1))

for i in range(df_test.shape[0]):
    current_route_duration = time_difference(outside_cluster, df_test.iloc[i]['time'])
    if current_route_duration > 0:  
        max_route_duration = max(routes_max_times[start_point])          
        late = max_route_duration < current_route_duration
        if(not late): 
            print("Current route duration ({} minutes) is smaller than max route duration ({} minutes) from {} to {} in history. This looks ok.".format(current_route_duration, max_route_duration, start_point, end_point))
        else:
            print("Current route duration ({} minutes) is larger than max route duration ({} minutes) from {} to {} in history. Sending a lost alert.".format(current_route_duration, max_route_duration, start_point, end_point))
            sys.exit(0)
    
breakStreet = ""   
if(len(test_transition_list)>1):
    end_point = test_transition_list[1]
    routes = transition_mat[start_point][end_point]["routes"]
    routes_streets = []
    for route in routes:
        routes_streets += route["streets"]
    
    routes_streets = set(routes_streets)
    print('streets {}'.format(routes_streets))
    found = True
    for elem in street_name:
        if elem not in routes_streets:
            found = False
            breakStreet = elem
            break
        
    if(not found): 
        print("street " + breakStreet + " not found in the history of routes from {} to {}. Sending a lost alert.".format(start_point, end_point))
        sys.exit(0)
    else:
        print("street " + str(street_name) + " was found in the history of routes from {} to {}. This looks ok.".format(start_point, end_point))
#        sys.exit(0)
        
total_number_of_clusters = len(df_clustered)
        
if(len(test_transition_list)<2):
    found = False
    routes_streets = []
    for i in range(total_number_of_clusters):
        routes = transition_mat[start_point][i]["routes"] 
        for route in routes:
            routes_streets += route["streets"]
    routes_streets = set(routes_streets)

    found = True
    for elem in street_name:
        if elem not in routes_streets:
            found = False
            breakStreet = elem
            break
        
    if(not found): 
        print("street " + breakStreet + " not found in the history of routes starting from {}. Sending a lost alert.".format(start_point))
        sys.exit(0)


