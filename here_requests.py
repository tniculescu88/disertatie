import pandas as pd
import json
import urllib.request


with open('transition_mat.json', 'r') as f:
    transition_mat = json.load(f)

with open('transition_list.json', 'r') as f:
    transition_list = json.load(f)
   
with open('sp_trans_list.json', 'r') as f:
    sp_trans_list = json.load(f)
    
with open('interest_points.json', 'r') as f:
    interest_points = json.load(f)
    
df_gps = pd.read_csv('user_location_with_snap_points.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  


json_decode = json.JSONDecoder()

results = []

for i in range(len(df_gps)):
    zone = df_gps.iloc[i]['zone']
    lat = df_gps.iloc[i]['snap_lat']
    lon = df_gps.iloc[i]['snap_lon']
    if (zone == -1 and lat != "not_filled" and lon != "not_filled"):
        bytesData = urllib.request.urlopen("https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?prox="+lat+"%2C"+lon+"%2C250&mode=retrieveAddresses&maxresults=1&gen=9&app_id=WWBAntTsRvOS0fscgPXJ&app_code=4NuAvXOIiG1gaP_vFTgu5Q").read()

        textData = bytesData.decode("utf8")

        answer = json_decode.decode(textData)
        print(i)
        print(answer)
        results.append({"index":i, "answer": answer})


with open('here_answers.json', 'w') as outfile:
    json.dump(results, outfile)

        
