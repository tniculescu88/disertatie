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
    
with open('google_answers.json', 'r') as f:
    google_answers = json.load(f)
    
    
        
df_gps = pd.read_csv('user_location_partially_written.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv') 

for item in google_answers:
    for i in range(len(item["indexes"])):
        if (i < len(item["answer"]["snappedPoints"])):
            index = item["indexes"][i]
            lat = item["answer"]["snappedPoints"][i]["location"]["latitude"]
            lon = item["answer"]["snappedPoints"][i]["location"]["longitude"]
            df_gps.loc[index,'snap_lat'] = lat
            df_gps.loc[index,'snap_lon'] = lon

            
df_gps.to_csv('user_location_with_snap_points.csv', index=False) 
