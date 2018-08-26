# import necessary modules
import pandas as pd, numpy as np, matplotlib.pyplot as plt, time
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from datetime import datetime as dt
from math import radians, cos, sin, asin, sqrt, atan2

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
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
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

def point_index_in_cluster(lat, lon, df_clustered, eps_rad):
    index = -1

    for i, cluster in enumerate(df_clustered.itertuples()):
        if distance(lat, lon, cluster[1], cluster[2]) < eps_rad:
            return i

    return index

def transition_matrix(df_gps, df_clustered, eps_rad):
    number_of_clusters = len(df_clustered)
    transitions = np.zeros((number_of_clusters, number_of_clusters))
    last = -1
    transition_list = list()

    for i, point in enumerate(df_gps.itertuples()):
        index = point_index_in_cluster(point[1], point[2], df_clustered, eps_rad)
        if index >= 0:
            if last == -1:
                last = index
                transition_list.append(index)
            elif index != last:
                transitions[last][index] += 1
                last = index
                transition_list.append(index)

    return transitions, transition_list

transition_mat, transition_list = transition_matrix(df_gps, df_clustered, radius)
print('transition matrix: {}'.format(transition_mat))
print('transition list: {}'.format(transition_list))

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

# show a map of the worldwide data points
fig, ax = plt.subplots(figsize=[11, 8])
rs_scatter = ax.scatter(df_clustered['lon'], df_clustered['lat'], c='m', edgecolor='None', alpha=0.3, s=120)
df_scatter = ax.scatter(df_gps['lon'], df_gps['lat'], c='k', alpha=0.5, s=3)
ax.set_title('Full data set vs DBSCAN reduced set')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.legend([df_scatter, rs_scatter], ['Full set', 'Reduced set'], loc='upper left')
plt.show()


