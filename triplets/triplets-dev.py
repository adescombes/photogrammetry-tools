#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import numpy as np
import os
from glob import glob

import sys
sys.path.append('../share')

SFM_MODEL = sys.argv[1]
SFM_MOUNT = sys.argv[2]
SFM_GROUPS = sys.argv[3]
SFM_PFILE = sys.argv[4]
model = '20191010-105434-20191010-00002-italy-venice-san_barnaba-0002-calle_lunga_de_san_barnaba'
sfm_data_path = SFM_MOUNT + "/" + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/sfm_data.json"

with open('/home/descombe/Desktop/test.txt', 'w') as f:
	f.write("%s" % sfm_data_path)
	f.close()

def sfm_info(model): # takes either a model or a full path to the json file as input
    sfm_data_path = SFM_MOUNT + "/" + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/sfm_data.json"
    if not os.path.exists(sfm_data_path):
        sfm_data_path = model 
        
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
    return pd.DataFrame([key_to_file_dict,key_to_pose_dict]).transpose().rename(columns = {0:'filename',1:'coor'})

def connections(model):
    models_0500 = glob('/media/gargantua/0500-plane/0000-image/*/*/*.txt')
    path = [x for x in models_0500 if model.split('-')[-1] in x]
    connections = []
    for connection in open(path[0], 'r').read().split('\n'):
        if connection is not '':
            connections.append(connection.split())
    return connections

def nearest_poses(point_ref, df, k): # point_ref = list of 3 coordinates
    dists = []
    x_b = point_ref[0]
    y_b = point_ref[1]
    z_b = point_ref[2]

    for i, row in df.iterrows():
        if type(row['coor']) is list:
            points = row['coor']
            x_a = points[0]
            y_a = points[1]
            z_a = points[2]

            dist = np.sqrt((x_b - x_a) * (x_b - x_a) + (y_b - y_a) * (y_b - y_a) + (z_b - z_a) * (z_b - z_a))
            if dist != 0:
                dists.append([dist,i])
    return [x[1] for x in sorted(dists)[:k]] # list of indexes of the k-closest of point_ref

def read_adj_mat(model):
    matches = []
    svg_file = SFM_MOUNT + "/" + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/matches/GeometricAdjacencyMatrix.svg"
    for line in open(svg_file, 'r').read().split('\n'):
        if "<rect" in line:
            x = ( np.float(line.split('"')[1]) / 5 )
            y = ( np.float(line.split('"')[3]) / 5 )
            matches.append([int(x),int(y)])
    return matches



idx_to_file_dict = sfm_info(SFM_MOUNT  + "/" + SFM_MODEL[0:4] + "/" + SFM_MODEL[4:8] + "/" + SFM_MODEL + "/" + "/systems/omvg/sfm_data.json").reset_index().filename.apply(lambda x : x.replace('.JPG','')).to_dict()
file_to_idx_dict = dict(zip(idx_to_file_dict.values(), idx_to_file_dict.keys()))

models_list = []
matches = []
links_list = []

for model in open(SFM_GROUPS, 'r').read().split('\n'):
    if model is not '':
        models_list.append(model)
        sfm_data = sfm_info(model)
        for x,y in read_adj_mat(model):
            x_general = file_to_idx_dict.get(sfm_data.iloc[x]['filename'])
            y_general = file_to_idx_dict.get(sfm_data.iloc[y]['filename'])
            matches.append([x_general, y_general])


for model1 in models_list:

    sfm_data1 = sfm_info(model1)

    for file1_2, model2 in connections(model1):

        filename = '_to_'.join(sorted([model1.split('-')[-1],model2]))

        if filename not in links_list: # si la connection n'a pas encore été traitée
            links_list.append(filename)
            img_list = []

            if len([x for x in models_list if model2 in x]) > 0: # si les photos ont bien été prises pour cet endroit
                model2_name = [x for x in models_list if model2 in x][0]
                sfm_data2 = sfm_info(model2_name)
                coor1_2 = [x for x in sfm_data1[sfm_data1['filename'] == file1_2]['coor']][0]
                filenames1_2 = sfm_data1.iloc[nearest_poses(coor1_2, sfm_data1, 20)]['filename']

                file2_1 = [x[0] for x in connections(model2_name) if model1.split('-')[-1] in x][0]
                coor2_1 = [x for x in sfm_data2[sfm_data2['filename'] == file2_1]['coor']][0]
                filenames2_1 = sfm_data2.iloc[nearest_poses(coor2_1, sfm_data2, 20)]['filename']
	
                """with open((SFM_MOUNT + "/"+ SFM_MODEL[0:4] + "/" + SFM_MODEL[4:8] + "/" + SFM_MODEL + "/systems/%s.txt" % filename), 'w') as f:

                    for f1 in filenames1_2:
                        f.write("%s\n" % f1)
                        img_list.append(f1)

                    for f2 in filenames2_1:
                        f.write("%s\n" % f2)
                        img_list.append(f2)

                    
                f.close()"""
                for f1 in filenames1_2:
                        for f2 in filenames2_1:
                            matches.append(sorted([file_to_idx_dict.get(f1), file_to_idx_dict.get(f2)]))

with open(SFM_PFILE, 'w') as f_matches:
	for match in matches:
		f_matches.write("%d %d\n" %(match[0], match[1]))
f_matches.close() 




