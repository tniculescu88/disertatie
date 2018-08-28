import pandas as pd
import json
import urllib.request
import time

with open('transition_mat.json', 'r') as f:
    transition_mat = json.load(f)

with open('transition_list.json', 'r') as f:
    transition_list = json.load(f)
   
with open('sp_trans_list.json', 'r') as f:
    sp_trans_list = json.load(f)
    
with open('interest_points.json', 'r') as f:
    interest_points = json.load(f)
    
with open('google_requests.json', 'r') as f:
    google_requests = json.load(f)
    
df_gps = pd.read_csv('user_location_partially_written.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  

json_decode = json.JSONDecoder()


for item in google_requests:
    bytesAnswer = urllib.request.urlopen(item["url"]).read()
    textAnswer = bytesAnswer.decode("utf8")
    item["answer"] = json_decode.decode(textAnswer)
    time.sleep(0.04)


with open('google_answers.json', 'w') as outfile:
    json.dump(google_requests, outfile)    
    
 