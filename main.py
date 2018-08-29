import pandas as pd
import json
import sys
import pdb
from datetime import datetime as dt
import datetime

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
    
df_gps = pd.read_csv('user_location_with_snap_points_and_streets.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  


def get_street_name(lat, lon):
  return "Strada Sibiu"

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
    sys.exit(0)
    
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
        print("street " + street_name + " was found in the history of routes from {} to {}. Looking ok.".format(start_point, end_point))
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