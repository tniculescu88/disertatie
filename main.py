import pandas as pd
import json
import sys
import pdb
from datetime import datetime as dt
import datetime
import urllib.request

if (len(sys.argv) != 2):
    print("example of usage: python main.py examples/example1.json")
    sys.exit(1)

examplefile = sys.argv[1]

with open(examplefile, 'r') as f:
    example = json.load(f)      
    
with open('transition_mat_with_streets.json', 'r') as f:
    transition_mat = json.load(f)

with open('transition_list.json', 'r') as f:
    transition_list = json.load(f)
   
with open('sp_trans_list.json', 'r') as f:
    sp_trans_list = json.load(f)
    
with open('interest_points.json', 'r') as f:
    interest_points = json.load(f)
    
with open('max_times.json', 'r') as f:
    max_times = json.load(f)
    
with open('schedule.json', 'r') as f:
    schedule = json.load(f)
    
    
df_gps = pd.read_csv('user_location_with_snap_points_and_streets.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  

day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

key = "AIzaSyB9kjlneNrld9gqGJb60ncVDOUuBdYa37s" 

json_decode = json.JSONDecoder()

def get_street_name_offline(lat, lon):
    if(lat == 44.4379451 and lon == 26.0596271):
       return "Șoseaua Grozăvești"
    if(lat == 44.4121317 and lon == 26.017119):
       return "Aleea Valea Salciei"
    if(lat == 44.4222703 and lon == 26.0352051):
       return "Drumul Taberei"
    
def get_street_name_online(lat, lon):
    google_url = "https://roads.googleapis.com/v1/snapToRoads?path="
    google_url += "{}".format(lat)
    google_url += ","
    google_url += "{}".format(lon)
    google_url += "&interpolate=false&key=" + key
    
    bytes_answer = urllib.request.urlopen(google_url).read()
    text_answer = bytes_answer.decode("utf8")
    google_answer = json_decode.decode(text_answer)
    
    print("google answered...")
    
    snapped_lat = google_answer["snappedPoints"][0]["location"]["latitude"]
    snapped_lon = google_answer["snappedPoints"][0]["location"]["longitude"]
    
    snapped_lat = "{}".format(snapped_lat)
    snapped_lon = "{}".format(snapped_lon)
    
    
    bytes_data = urllib.request.urlopen("https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?prox="+snapped_lat+"%2C"+snapped_lon+"%2C250&mode=retrieveAddresses&maxresults=1&gen=9&app_id=WWBAntTsRvOS0fscgPXJ&app_code=4NuAvXOIiG1gaP_vFTgu5Q").read()

    text_data = bytes_data.decode("utf8")
    here_answer = json_decode.decode(text_data)
    
    print("here answered...")
    
    address = here_answer["Response"]["View"][0]["Result"][0]["Location"]["Address"]
    street = "notReturnedByHere"
    if ("Street" in address):
        street = address["Street"]
    
    return street

def get_street_name(lat, lon): 
    return get_street_name_online(lat, lon)
  
#import pdb; pdb.set_trace()

outside_cluster = "cluster_left" in example

start_point = example["start_point"]
lat = example["lat"]
lon = example["lon"]
street_name = ""

if(outside_cluster):
    street_name = get_street_name(lat, lon) 
    
def time_difference(date_time1, date_time2):
    d1 = datetime.datetime.strptime(date_time1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(date_time2, '%Y-%m-%d %H:%M:%S')
    return (d2 - d1).total_seconds() / 60

if(not outside_cluster):
    time_in_cluster = time_difference(example["cluster_entered"], example["time"])
    print("minutes in cluster: {}".format(time_in_cluster))
    if(time_in_cluster > max_times[start_point]):
        print("{} minutes spent in current point {} are more than the history max ({} minutes) for this point. Sending an alert.".format(time_in_cluster, start_point, max_times[start_point]))
        sys.exit(0)
    else:
        print("{} minutes spent in current point {} are less than the history max ({} minutes) for this point. This looks ok.".format(time_in_cluster, start_point, max_times[start_point]))


if(not outside_cluster):
    if(schedule[start_point] == "any_time_is_ok"):
        print("At this interest point {}, the user can be at any time during the day. This looks ok.".format("start_point"))
    else:
        current_time = datetime.datetime.strptime(example["time"], '%Y-%m-%d %H:%M:%S')
        weekday = current_time.weekday()
        hour = current_time.hour
        
        if(schedule[start_point][weekday][hour] == "never"):
            print("Never before this interest point {} has been visited on a {} and between {} and {}. Sending an alert.".format(start_point, day_names[weekday], hour, hour + 1))
            sys.exit(0)
        else:
            print("This interest point {} has been visited before on a {} and and between {} and {}. This looks ok.".format(start_point, day_names[weekday], hour, hour + 1))
        
    
if("end_point" in example):
    end_point = example["end_point"]
    routes = transition_mat[start_point][end_point]["routes"]
    found = False
    for route in routes:
        for street in route["streets"]:
            if(street == street_name):
                found = True
    if(not found): 
        print("street " + street_name + " not found in the history of routes from {} to {}. Sending a lost alert.".format(start_point, end_point))
        sys.exit(0)
    else:
        print("street " + street_name + " was found in the history of routes from {} to {}. This looks ok.".format(start_point, end_point))
        sys.exit(0)
        
number_of_clusters = len(df_clustered)
        
if(not("end_point" in example)):
    found = False
    
    for i in range(number_of_clusters):
        routes = transition_mat[start_point][i]["routes"] 
        for route in routes:
            for street in route:
                if(street == street_name):
                    found = True
    
    if(not found): 
        print("street " + street_name + " not found in the history of routes starting from {}. Sending a lost alert.".format(start_point))
        sys.exit(0)
     

import pdb; pdb.set_trace()