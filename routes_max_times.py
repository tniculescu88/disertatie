import pandas as pd
import json


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


number_of_clusters = len(df_clustered)

routes_max_times = [[0 for x in range(number_of_clusters)] for y in range(number_of_clusters)]

for i in range(number_of_clusters):
    for j in range(number_of_clusters):
        max_route_duration = 0
        for route in transition_mat[i][j]["routes"]:
             if(route["route_duration"] > max_route_duration):
                 max_route_duration = route["route_duration"]
        routes_max_times[i][j] = max_route_duration
        
        
with open('routes_max_times.json', 'w') as outfile:
    json.dump(routes_max_times, outfile)
        
