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
    
df_gps = pd.read_csv('user_location_with_snap_points_and_streets.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')

number_of_clusters = len(df_clustered)

for i in range(number_of_clusters):
    for j in range(number_of_clusters):
        routes = transition_mat[i][j]["routes"]
        for route in routes:
            route["streets"] = []
            for index in range(route["route_start"] + 1, route["route_end"]):
                street = df_gps.iloc[index]['street']
                zone = df_gps.iloc[index]['zone']
                if(zone == -1):
                    if(len(route["streets"]) == 0 or route["streets"][-1] != street):
                        if(street != "notReturnedByHere" and street != "not_filled"):
                            route["streets"].append(street)
                else:
                    print("eroare, ar trebui sa fie zona -1")


with open('transition_mat_with_streets.json', 'w') as outfile:
    json.dump(transition_mat, outfile)