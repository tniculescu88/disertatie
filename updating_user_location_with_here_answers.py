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
    
with open('here_answers.json', 'r') as f:
    here_answers = json.load(f)
    
df_gps = pd.read_csv('user_location_with_snap_points.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  


for item in here_answers:
    address = item["answer"]["Response"]["View"][0]["Result"][0]["Location"]["Address"]
    street = "notReturnedByHere"
    if ("Street" in address):
        street = address["Street"]
    df_gps.loc[item["index"],'street'] = street
    
    
df_gps.to_csv('user_location_with_snap_points_and_streets.csv', index=False)