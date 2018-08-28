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
    
df_gps = pd.read_csv('user_location_partially_written.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  


print('loaded transition matrix is {}'.format(transition_mat))
print('loaded transition list is {}'.format(transition_list))
print('loaded special transition list is {}'.format(sp_trans_list)) 

number_of_clusters = len(df_clustered)

'''
max_route = 0

for i in range(number_of_clusters):
    for j in range(number_of_clusters):
        print("item: {}".format(transition_mat[i][j]))
        for k in range(len(transition_mat[i][j]["routes"])):
            if(max_route < transition_mat[i][j]["routes"][k]["route_size"]):
                max_route = transition_mat[i][j]["routes"][k]["route_size"]
                
                
print(max_route)
'''


requests = [{"lats":[], "lons":[], "indexes":[], "url":""}]

for index, row in df_gps.iterrows():
    if(row["zone"] == -1):
        if(len(requests[-1]["indexes"]) == 100):
            requests.append({"lats":[], "lons":[], "indexes":[], "url":""})
        requests[-1]["indexes"].append(index)
        requests[-1]["lats"].append(df_gps.loc[index, 'lat'])
        requests[-1]["lons"].append(df_gps.loc[index, 'lon'])

key = "AIzaSyB9kjlneNrld9gqGJb60ncVDOUuBdYa37s"        
                    
for item in requests:
    item["url"] = "https://roads.googleapis.com/v1/snapToRoads?path="
    for j in range(len(item["indexes"])):
        item["url"] += "{}".format(item["lats"][j])
        item["url"] += ","
        item["url"] += "{}".format(item["lons"][j])
        if(j < len(item["indexes"])-1):
            item["url"] += "|"
    item["url"] += "&interpolate=true&key=" + key
    
    del item['lats']
    del item['lons']
    
    
with open('goole_requests.json', 'w') as outfile:
    json.dump(requests, outfile)
         
        