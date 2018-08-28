# import necessary modules
import pandas as pd, numpy as np, matplotlib.pyplot as plt, time
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from datetime import datetime as dt
from math import radians, cos, sin, asin, sqrt, atan2
import datetime
import json

cluster_min_time = 5 #minim 5 minute in acelasi cluster
# load the full location history json file downloaded from google
df_gps = pd.read_csv('user_location.csv')
print('There are {:,} rows'.format(len(df_gps)))

# define the number of kilometers in one radian
kms_per_radian = 6371.0088

def distance(lat1, lon1, lat2, lon2):
    radius = 6371.0088 # km in one radian

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c
    
    return d

def get_centermost_point(cluster):
    x = 0
    y = 0
    for point in cluster:
        x += point[0]
        y += point[1]
    x = x/len(cluster)
    y = y/len(cluster)
    centroid = (x,y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)

def dbscan_reduce(df, epsilon, x='lon', y='lat'):
    start_time = time.time()
    # represent points consistently as (lat, lon) and convert to radians to fit using haversine metric
    coords = df[[y, x]].values 
    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    
    clusters = pd.Series([coords[cluster_labels==n] for n in range(num_clusters)])
    
    index_list = []
    for i, cluster in enumerate(clusters):
        if (len(cluster) < 70):
            index_list.append(i)
    clusters = clusters.drop(index=index_list)
  
    # find the point in each cluster that is closest to its centroid
    centermost_points = clusters.map(get_centermost_point)

    # unzip the list of centermost points (lat, lon) tuples into separate lat and lon lists
    lats, lons = zip(*centermost_points)
    rep_points = pd.DataFrame({x:lons, y:lats})
    rep_points.tail()
    
    # pull row from original data set where lat/lon match the lat/lon of each row of representative points
    rs = rep_points.apply(lambda row: df[(df[y]==row[y]) & (df[x]==row[x])].iloc[0], axis=1)
    
    # all done, print outcome
    message = 'Clustered {:,} points down to {:,} points, for {:.2f}% compression in {:,.2f} seconds.'
    print(message.format(len(df), len(rs), 100*(1 - float(len(rs)) / len(df)), time.time()-start_time))    
    return rs

# first cluster the full gps location history data set coarsely, with epsilon=0.1km in radians
radius = 0.1
eps_rad = radius / kms_per_radian
df_clustered = dbscan_reduce(df_gps, epsilon=eps_rad)

def point_index_in_cluster(lat, lon, df_clustered):
    index = -1

    for i, cluster in enumerate(df_clustered.itertuples()):
        if distance(lat, lon, cluster[1], cluster[2]) < radius:
            return i

    return index

def transition_matrix(df_gps, df_clustered):
    number_of_clusters = len(df_clustered)
    transitions = [[{"count":0} for x in range(number_of_clusters)] for y in range(number_of_clusters)] 
    last = -1
    transition_list = list()
    sp_trans_list = list()

    for i, point in enumerate(df_gps.itertuples()):
        p_index = point_index_in_cluster(point[1], point[2], df_clustered)
        if p_index >= 0: 
            if last == -1:
                last = p_index
                transition_list.append(p_index)
                sp_trans_list.append([i, i])
            elif p_index == last:
                sp_trans_list[len(sp_trans_list) - 1][1] = i
            elif p_index != last:
                transitions[last][p_index]["count"] = transitions[last][p_index]["count"] + 1
                last = p_index
                transition_list.append(p_index)
                sp_trans_list.append([i, i])
            

    return transitions, transition_list, sp_trans_list

def time_difference(date_time1, date_time2):
    d1 = datetime.datetime.strptime(date_time1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(date_time2, '%Y-%m-%d %H:%M:%S')
    return (d2 - d1).total_seconds() / 60

transition_mat, transition_list, sp_trans_list = transition_matrix(df_gps, df_clustered)
print('transition matrix: {}'.format(transition_mat))
print('transition list: {}'.format(transition_list))
print('sp_trans_list: {}'.format(sp_trans_list))

index_with_problems = []

for i, sList in enumerate(sp_trans_list):
    if time_difference(df_gps.iloc[sList[0]]['time'], df_gps.iloc[sList[1]]['time']) < cluster_min_time:
        index_with_problems.append(i)

print('index with problems {}'.format(index_with_problems))

for index in sorted(index_with_problems, reverse=True):
    del transition_list[index]
    del sp_trans_list[index]

print('now transition list is {}'.format(transition_list))
print('now special transition list is {}'.format(sp_trans_list))


total_route_size = 0

#filtering the transition matrix
number_of_clusters = len(df_clustered)
transition_mat = [[{"count":0, "routes":[]} for x in range(number_of_clusters)] for y in range(number_of_clusters)] 
for i in range(0, len(transition_list) - 1):
    source = transition_list[i]
    destination = transition_list[i+1]
    if(source != destination):
        transition_mat[source][destination]["count"] += 1
        start_index = sp_trans_list[i][1]
        end_index = sp_trans_list[i+1][0]
        start_time = df_gps.values[start_index][2]
        end_time = df_gps.values[end_index][2]
        route_size = end_index - start_index
        route_duration = time_difference(start_time, end_time)
        route = {
            "start_index": start_index, 
            "end_index": end_index, 
            "start_time": start_time, 
            "end_time": end_time, 
            "route_size": route_size,
            "route_duration": route_duration
        }
        total_route_size += route_size
        transition_mat[source][destination]["routes"].append(route)
    
   

    
    
    
print('now transition matrix is: {}'.format(transition_mat))

print('total route size: {}'.format(total_route_size))



total_interest_records = 0
for point in sp_trans_list:
    total_interest_records += point[1] - point[0]
print('total records inside interest clusters: {}'.format(total_interest_records))
    
 

# for i,sList in enumerate(sp_trans_list):
#     if sList[1] == -1:
#         print ('index with problems:{}'.format(i))
#         print ('transitionList[{}] = {}'.format(i-1,transition_list[i-1]))
#         print ('transitionList[{}] = {}'.format(i,transition_list[i]))
#         print ('sp_transitionList[{}] = {}'.format(i-1,sp_trans_list[i-1]))
#         print ('sp_transitionList[{}] = {}'.format(i,sp_trans_list[i]))
#         print ('sp_transitionList[{}] = {}'.format(i+1,sp_trans_list[i+1]))

'''
print(df_clustered)
print('sth:{}'.format(df_clustered[['lat', 'lon']]))
lat_lon = df_clustered[['lat', 'lon']]
all_lat_lon = df_gps[['lat', 'lon']]
print('lat and lon: {}'.format(lat_lon.iloc[0]['lat']))
print('all lat lon: {}'.format(all_lat_lon))
coords_1 = (lat_lon.iloc[0]['lat'], lat_lon.iloc[0]['lon'])
coords_2 = (all_lat_lon.iloc[0]['lat'], all_lat_lon.iloc[0]['lon'])
print('first: {} and second: {}'.format(coords_1, coords_2))
print('distance is: {}'.format(distance(lat_lon.iloc[0]['lat'], lat_lon.iloc[0]['lon'], all_lat_lon.iloc[0]['lat'], all_lat_lon.iloc[0]['lon'])))
'''
# save to csv
df_clustered.to_csv('user-location-clustered.csv', index=False, encoding='utf-8')


with open('transition_mat.json', 'w') as outfile:
    json.dump(transition_mat, outfile)
    
with open('transition_list.json', 'w') as outfile:
    json.dump(transition_list, outfile)
    
with open('sp_trans_list.json', 'w') as outfile:
    json.dump(sp_trans_list, outfile)

print("adding the zones...")    
    
df_gps['zone'] = -1
    
for i in range(len(sp_trans_list)):
    start = sp_trans_list[i][0]
    end = sp_trans_list[i][1]
    zone = transition_list[i]
    for j in range(start, end + 1):
        df_gps.loc[j,'zone'] = zone
    
df_gps.to_csv('user_location_with_zones.csv', index=False) 

# show a map of the worldwide data points
fig, ax = plt.subplots(figsize=[11, 8])
rs_scatter = ax.scatter(df_clustered['lon'], df_clustered['lat'], c='m', edgecolor='None', alpha=0.3, s=120)
df_scatter = ax.scatter(df_gps['lon'], df_gps['lat'], c='k', alpha=0.5, s=3)
ax.set_title('Full data set vs DBSCAN reduced set')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.legend([df_scatter, rs_scatter], ['Full set', 'Reduced set'], loc='upper left')
plt.show()


