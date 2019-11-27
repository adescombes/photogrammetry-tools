"""
This program aims at making a map with folium showing all the camera poses in a 3D model created with photogrammetry.
A marker at each position will show the image taken and its filename.
IN : - PLY file, in a repository containing the images used for photogrammetry, the sfm_data.json file of its metadata (output of the openMVG pipeline),
		as well as the selection of points (1. of the model, 2. of a cadastre map) used for georeferencing.
	- the EPSG used for georeferencing
OUT : a file called camera_poses.html in the same repository.
"""

import pandas as pd
import numpy as np
import folium
import os
import subprocess
import json
from folium import IFrame
import base64
import sys
import pyproj
from pyproj import Proj, transform, Transformer
from least_squares_matching import least_squares_matching

model = sys.argv[1] 
epsg = sys.argv[2]
version = model.split('/')[-2]
path = '/'.join(model.split('/')[:-1]) 

transformer = Transformer.from_crs(int(epsg), 4326)


coor_model_file = path + "/geodesy/points_model"
coor_cadastre_file = path + "/geodesy/points_cadastre_epsg"+epsg

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

F,R,t = least_squares_matching(coor_model_file, coor_cadastre_file)

# Apply transformation to camera poses
for key, camera_pose in key_to_pose_dict.items():
    #transf_coor = {key: list(np.matmul(np.transpose(R), np.subtract(F * np.array(camera_pose), t)))}
    x,y,z = list(np.matmul(np.transpose(R), np.subtract(F * np.array(camera_pose), t)))
    yy,xx,zz = transformer.transform(x,y,z)
    transf_coor = {key: [xx,yy,zz]}
    key_to_pose_dict.update(transf_coor)

# get missing files (images that have not been used for the 3D reconstruction)
if len(views_keys) > len(extrinsics_keys):
    with open(path + '/systems/missing_files.txt', 'w') as f_out:
        for key, filename in key_to_file_dict.items():
            if key not in extrinsics_keys:
                f_out.write('%s.tif\n' % filename)



os.system("/home/descombe/Desktop/photogrammetry-tools/make_thumbnails %s/images tif" % path)

# map centered on Venice
m = folium.Map(location=[45.434285, 12.338791], zoom_start=14, max_zoom=50, tiles = 'cartodbpositron')


for key, coor in key_to_pose_dict.items():
    file = key_to_file_dict.get(key)
    Filename = path + "/thumbnails/" + file + ".jpg"
    
    # insert thumbnail in marker's popup
    encoded = base64.b64encode(open(Filename, 'rb').read())
    html=('<img src="data:image/tif;base64,{}"><b> %s </b>' % file).format 
    iframe = IFrame(html(encoded.decode('UTF-8')), width=500, height=350)
    popup = folium.Popup(iframe, max_width=1000)
    icon = folium.Icon(color="red", icon = None)
    
    # transform coordinates of marker from Monte Mario 2 to Mercator
    #transformer = Transformer.from_crs(3004, 4326)
    #lat, lon = transformer.transform(row['X'], row['Y'])
    lat = coor[1]
    lon = coor[0]
    marker = folium.Marker(location=[lat, lon], popup=popup, icon=icon)
    marker.add_to(m)
    
m.save('%s/geodesy/camera_poses.html' % path)



