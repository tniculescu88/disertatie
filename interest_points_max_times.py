import pandas as pd
import json
import datetime


def time_difference(date_time1, date_time2):
    d1 = datetime.datetime.strptime(date_time1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(date_time2, '%Y-%m-%d %H:%M:%S')
    return (d2 - d1).total_seconds() / 60


with open('transition_mat.json', 'r') as f:
    transition_mat = json.load(f)

with open('transition_list.json', 'r') as f:
    transition_list = json.load(f)
   
with open('sp_trans_list.json', 'r') as f:
    sp_trans_list = json.load(f)
    
with open('interest_points.json', 'r') as f:
    interest_points = json.load(f)
    
df_gps = pd.read_csv('user_location_with_zones.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  



df_gps["snap_lat"] = "not_filled";
df_gps["snap_lon"] = "not_filled";
df_gps["street"] = "not_filled";

max_times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

for i in range(len(sp_trans_list)):
    start = sp_trans_list[i][0]
    end = sp_trans_list[i][1]
    zone = transition_list[i]
    zone_start_time = df_gps.loc[start, 'time']
    zone_end_time = df_gps.loc[end, 'time']
    diff = time_difference(zone_start_time, zone_end_time)
    if(diff > max_times[zone]):
        max_times[zone] = diff
        
with open('max_times.json', 'w') as outfile:
    json.dump(max_times, outfile)
        
        


        
