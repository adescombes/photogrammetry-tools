import json
import pandas as pd
import numpy as np
import os
from glob import glob
import sys

SFM_MOUNT = '/media/gargantua/1000-plane/0000-sfm/'
model = sys.argv[1]

sfm_data_path = SFM_MOUNT + "/" + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/sfm_data.json"
if not os.path.exists(sfm_data_path):
    sfm_data_path = model 

with open(sfm_data_path) as sfm_data:
    data = json.load(sfm_data)
    views = data['views']
    extrinsics = data['extrinsics']
    intrinsics = data['intrinsics']
    structure = data['structure']
    control_points = data['control_points'] # sert pas à grand chose pour l'instant

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

# get missing files (images that have not been used for the 3D reconstruction)
if len(views_keys) > len(extrinsics_keys):
    for key, filename in key_to_file_dict.items():
        if key not in extrinsics_keys:
            print(filename + '.tif')

