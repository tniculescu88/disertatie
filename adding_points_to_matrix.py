import pandas as pd
import json


with open('transition_mat_with_streets.json', 'r') as f:
    transition_mat = json.load(f)

with open('transition_list.json', 'r') as f:
    transition_list = json.load(f)
   
with open('sp_trans_list.json', 'r') as f:
    sp_trans_list = json.load(f)
    
with open('interest_points.json', 'r') as f:
    interest_points = json.load(f)
    
df_gps = pd.read_csv('user_location_partially_written.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  


number_of_clusters = len(df_clustered)

for i in range(number_of_clusters):
    for j in range(number_of_clusters):
        routes = transition_mat[i][j]["routes"]
        for route in routes:
            route["points"] = []
            for index in range(route['route_start'], route['route_end']):
                route["points"].append({'lat':df_gps.iloc[index]['lat'],'lon':df_gps.iloc[index]['lat'],'index':index})

with open('transition_mat_with_streets_and_points.json', 'w') as outfile:
    json.dump(transition_mat, outfile)
