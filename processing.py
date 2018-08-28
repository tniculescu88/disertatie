import pandas as pd
import json


with open('transition_mat.json', 'r') as f:
    transition_mat = json.load(f)

with open('transition_list.json', 'r') as f:
    transition_list = json.load(f)
   
with open('sp_trans_list.json', 'r') as f:
    sp_trans_list = json.load(f)
    
df_gps = pd.read_csv('user_location.csv')  

df_clustered = pd.read_csv('user-location-clustered.csv')  
    

print('loaded transition matrix is {}'.format(transition_mat))
print('loaded transition list is {}'.format(transition_list))
print('loaded special transition list is {}'.format(sp_trans_list))    
    
