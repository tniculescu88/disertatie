import pandas as pd
import json
import datetime


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


def time_difference(date_time1, date_time2):
    d1 = datetime.datetime.strptime(date_time1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(date_time2, '%Y-%m-%d %H:%M:%S')
    return (d2 - d1).total_seconds() / 60

day_squedule = Matrix = [["never" for x in range(24)] for y in range(7)]     
    
schedule = [day_squedule]*10


for i in range(len(sp_trans_list)):
    start = sp_trans_list[i][0]
    end = sp_trans_list[i][1]
    zone = transition_list[i]
    
    
    if(schedule[zone] == "any_time_is_ok"):
        continue
    
    zone_start_time = df_gps.loc[start, 'time']
    zone_end_time = df_gps.loc[end, 'time']
    diff = time_difference(zone_start_time, zone_end_time)
    start_time = datetime.datetime.strptime(zone_start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.datetime.strptime(zone_end_time, '%Y-%m-%d %H:%M:%S')
    
    if(start_time.day != end_time.day):
        schedule[zone] = "any_time_is_ok"
    else:
        for hour in range(start_time.hour, end_time.hour + 1):
            schedule[zone][start_time.weekday()][hour] = "vizited"
    

with open('schedule.json', 'w') as outfile:
    json.dump(schedule, outfile)



