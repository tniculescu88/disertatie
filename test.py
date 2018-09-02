import pandas as pd, numpy as np, matplotlib.pyplot as plt, time
from geopy.distance import great_circle
# from shapely.geometry import MultiPoint
from datetime import datetime as dt
from math import radians, cos, sin, asin, sqrt, atan2

# define the number of kilometers in one radian
kms_per_radian = 6371.0088

radius = 0.1
eps_rad = radius / kms_per_radian

def distance(lat1, lon1, lat2, lon2):
    radius = 6371.0088 # km in one radian

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c
    
    return d

def point_index_in_cluster(lat, lon, df_clustered):
    index = -1

    for i, cluster in enumerate(df_clustered.itertuples()):
        if distance(lat, lon, cluster[1], cluster[2]) < radius:
            return i

    return index
	
df_test = pd.read_csv('./examples/example1.csv')
df_clustered = pd.read_csv('user-location-clustered.csv')
kPOI = 2 # afi point of interest
aList = []
for i in range(df_test.shape[0]):
	aList.append(point_index_in_cluster(df_test.iloc[i]['lat'], df_test.iloc[i]['lon'], df_clustered))
	result = distance(df_test.iloc[i]['lat'], df_test.iloc[i]['lon'], df_clustered.iloc[kPOI]['lat'], df_clustered.iloc[kPOI]['lon'] )
	

	
