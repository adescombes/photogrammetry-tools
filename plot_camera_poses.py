import json
import pandas as pd
import numpy as np
import sys
from mpl_toolkits.mplot3d import Axes3D 
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (12, 9)
plt.rcParams["figure.constrained_layout.use"] = True


model = sys.argv[1]  # in : name of the *-vodom.ply file
version = model.split('/')[-2]
path = '/'.join(model.split('/')[:-1]) 
sfm_data_path = path + "/systems/omvg/sfm_data.json"


with open(sfm_data_path) as sfm_data:
    data = json.load(sfm_data)
    views = data['views']
    extrinsics = data['extrinsics']
    
views_keys = []
files = []
for view in views:
    views_keys.append(view['key'])
    files.append(view['value']['ptr_wrapper']['data']['filename'].replace('.tif',''))
    
key_to_file_dict = dict(zip(views_keys,files))
    
extrinsics_keys = []
camera_poses = []
for extrinsic in extrinsics:
    extrinsics_keys.append(extrinsic['key'])
    camera_poses.append(extrinsic['value']['center'])
    
key_to_pose_dict = dict(zip(extrinsics_keys,camera_poses))


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for key, coor in key_to_pose_dict.items():
    x = coor[0]
    y = coor[1]
    z = coor[2]
    label = key_to_file_dict.get(key)
    ax.scatter(x, y, z)
    ax.text(x, y, z, label, fontsize = 6)

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()
fig.savefig('figures/%s.png' % '-'.join([version.split('-')[0],version.split('-')[-1]]), dpi = 150)






