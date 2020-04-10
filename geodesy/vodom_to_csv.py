"""
This program can be used to display the estimated camera poses of a georeferenced model in a GIS.
IN : PLY file, in a repository containing the sfm_data.json file of its metadata (output of the openMVG pipeline),
as well as the selection of points (1. of the model, 2. of a cadastre map) which was to georeference it.
OUT : a CSV file with the latitude, longitude and filename associated to each camera pose.
The .csv file can be imported in a GIS in order to check if the 3D model is well georeferenced, by comparing it with
a cadastre map.
"""
import json
import pandas as pd
import numpy as np
import sys
import click

sys.path.append('../share')
from least_squares_matching import least_squares_matching

@click.command()
@click.option('--model', help='path to the PLY file of the model')
@click.option('--epsg', help='EPSG in which the model must be displayed. the camera poses will be stored in a CSV file')

def vodom_to_csv(model, epsg):
    version = model.split('/')[-2]
    path = '/'.join(model.split('/')[:-1]) 
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

    for key, camera_pose in key_to_pose_dict.items():
        transf_coor = {key: list(np.matmul(np.transpose(R), np.subtract(F * np.array(camera_pose), t)))}
        key_to_pose_dict.update(transf_coor)

    for key, coor in key_to_pose_dict.items():
        file = key_to_file_dict.get(key)

    csv_path = path + "/geodesy/" + version + "-epsg" + epsg + ".csv"
    with open(csv_path, 'w') as f_out:
        f_out.write('X,Y,filename\n')
        for key, camera_pose in key_to_pose_dict.items():
            x,y,_ = camera_pose
            filename = key_to_file_dict.get(key)
            f_out.write('%f,%f,%s\n' %(x,y,filename))
            
            
if __name__ == '__main__':
    vodom_to_csv()
