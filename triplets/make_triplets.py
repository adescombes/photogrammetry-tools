import pandas as pd
import json
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
from tqdm import tqdm
import sys
sys.path.append('/home/descombe/Desktop/point-cloud-segmentation/wide-angle-images/src_df/')
from utils import get_sfm_data_as_dict, views_inverse_mapping, _convert_list_to_dict
plt.rcParams["figure.figsize"] = (25,25)

def read_adj_mat(svg_file):
    matches = []
    for line in open(svg_file, 'r').read().split('\n'):
        if "<rect" in line:
            x = ( np.float(line.split('"')[1]) / 5 )
            y = ( np.float(line.split('"')[3]) / 5 )
            matches.append([int(x),int(y)])
    return matches

"""
matches = read_adj_mat(svg_file)

min_ = min(min(matches, key=min))
max_ = max(max(matches, key=max))
dim = max_ - min_ + 1
"""

general_matches = []
mount_sfm = '/media/gargantua/1000-plane/0000-sfm/'
mount_img = '/media/gargantua/0500-plane/0000-image/'
models_dict = {}
matches_dict = {}
models_list = '/home/descombe/Desktop/san_giorgio_ground_floor'
out_dir = '/home/descombe/Desktop/photogrammetry-tools/triplets/san_giorgio/'


sfm_path_dict = {}

for line in open(models_list, 'r').read().strip().split('\n')[1:]:
    
    models = line.split(' ')
    general_model = models[0]
    models_dict.update({general_model : models[1:]})
    
    
    # create sfm_data.json files
    for model in models:
        sfm_path = mount_sfm + "/" + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/" 
        img_path = mount_img + "/" + model[0:4] + "/" + model[4:8] + "/" + model
        if not os.path.exists(sfm_path):
            if len(glob(img_path + "/*.JPG")) > 0:
                #os.system('openMVG_main_SfMInit_ImageListing -i %s -f 3378.7 -o %s/' % (img_path, out_dir))
                #shutil.move('%s/sfm_data.json' % out_dir, '%s/sfm_data_%s.json' % (out_dir, model.split('-')[-1]))
                sfm_path_dict.update({model : '%s/sfm_data_%s.json' % (out_dir, model.split('-')[-1])})
            else: 
                print('Given path does not exist')
        else:
            sfm_path_dict.update({model : sfm_path + "sfm_data.json"})
        
matches_dict = {}
for general_model, models in tqdm(models_dict.items()):

    for model in models:
        sfm_path = mount_sfm + "/" + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/"
        matches = []
        if os.path.exists(sfm_path):
            adj_mat_path = sfm_path + "matches/GeometricAdjacencyMatrix.svg" 
            json_path = sfm_path + "sfm_data.json" 
            local_matches = read_adj_mat(adj_mat_path)
            _, views_dict, _, _  = get_sfm_data_as_dict(json_path)
            for match in local_matches:
                filename1 = views_dict.get(match[0])['ptr_wrapper']['data']['filename'].split('.')[0]
                filename2 = views_dict.get(match[1])['ptr_wrapper']['data']['filename'].split('.')[0]
                matches.append([filename1, filename2])
            
        else:
            json_path = sfm_path_dict.get(model)
            _, views_dict, _, _  = get_sfm_data_as_dict(json_path)
            views_reversed = views_inverse_mapping(views_dict)
            views = list(views_reversed.keys())
            for i in range(len(views) - 1):
                for j in range(i + 1, len(views)):
                    matches.append([views[i], views[j]])
            
            
        matches_dict.update({model: matches})
            
            
matches_names = []
value = 1

for general_model, models in tqdm(models_dict.items()):
    print(general_model)
    print(len(models))
    general_matches = []
    _, general_views_dict, _, _ = get_sfm_data_as_dict(sfm_path_dict.get(general_model))
    general_indices = views_inverse_mapping(general_views_dict)
    general_matches_filename = '/home/descombe/Desktop/photogrammetry-tools/triplets/san_giorgio/%s_matches.txt' % general_model.split('-')[-1]
    general_matrix = np.zeros((max(general_indices.values())+1, max(general_indices.values())+1))
    general_matrix_filename = '/home/descombe/Desktop/photogrammetry-tools/triplets/san_giorgio/%s_matches.dat' % general_model.split('-')[-1]
    
    
    val = 1

    # add matches for each model with itself
    for model in models:
        print(len(matches_dict.get(model)))
        for match in matches_dict.get(model):
            general_matches.append([general_indices.get(match[0]), general_indices.get(match[1]), val])
        val += 1
        

    # add matches for each first model with the others (the first one sees the others)

    base_model = models[0]
    linked_models = models[1:]

    _, base_views_dict, _, _ = get_sfm_data_as_dict(sfm_path_dict.get(base_model))
    base_names = list(views_inverse_mapping(base_views_dict).keys())

    for linked_model in linked_models:

        _, linked_views_dict, _, _ = get_sfm_data_as_dict(sfm_path_dict.get(linked_model))
        linked_names = list(views_inverse_mapping(linked_views_dict).keys())

        for i in range(len(base_names)):
            for j in range(len(linked_names)):
                general_matches.append([general_indices.get(base_names[i]), general_indices.get(linked_names[j]), value]) 

    with open(general_matches_filename, 'w') as f:
        for match in general_matches:
            match1 = min(match[0:2])
            match2 = max(match[0:2])
            if match1 != match2:
                f.write('%d %d\n' %(match1, match2))
                general_matrix[match1, match2] = match[2]
                
    np.savetxt(general_matrix_filename, general_matrix, fmt='%d')
        