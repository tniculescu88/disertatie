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


print('loaded transition matrix is {}'.format(transition_mat))
print('loaded transition list is {}'.format(transition_list))
print('loaded special transition list is {}'.format(sp_trans_list)) 



df_gps["snap_lat"] = "not_filled";
df_gps["snap_lon"] = "not_filled";
df_gps["street"] = "not_filled";

for i in range(len(sp_trans_list)):
    start = sp_trans_list[i][0]
    end = sp_trans_list[i][1]
    zone = transition_list[i]
    for j in range(start, end + 1):
        df_gps.loc[j,'snap_lat'] = df_clustered.loc[zone, 'lat']
        df_gps.loc[j,'snap_lon'] = df_clustered.loc[zone, 'lon']
        df_gps.loc[j,'street'] = interest_points[zone]
        
df_gps.to_csv('user_location_partially_written.csv', index=False) 

        

