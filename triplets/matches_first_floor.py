import pandas as pd
import json
from glob import glob
import numpy as np
import os
import shutil
from tqdm import tqdm
import sys
sys.path.append('/home/descombe/Desktop/point-cloud-segmentation/wide-angle-images/src_df/')
from utils import get_sfm_data_as_dict, views_inverse_mapping, _convert_list_to_dict

models_file = open('/home/descombe/Desktop/links_san_giorgio_first_floor', 'r').read().strip().split('\n')
models_links = [x.strip().split() for x in models_file]
models_name = list(set([x for x in ' '.join(models_file).split(' ')]))

mount_path = '/media/gargantua/0500-plane/0000-image/2020/'
general_folder = mount_path + '/0714/20200714-00001-italy-venice-isola_san_giorgio-0001-first_floor/'

def get_indices(model_name: str):
    
    folder_path = mount_path + model_name[4:8] + "/" + model_name
    json_file = './san_giorgio_image_listing/sfm_data_%s.json' % model_name.split('-')[-1]
    if not os.path.exists(json_file):
        os.system('openMVG_main_SfMInit_ImageListing -i %s -f 3378.7 -o ./san_giorgio_image_listing' % folder_path)
        shutil.move('./san_giorgio_image_listing/sfm_data.json', json_file)
        
    return json_file

"""--- general indices ---"""

json_file = get_indices('20200714-00001-italy-venice-isola_san_giorgio-0001-first_floor')

_, views_dict, _, _ = get_sfm_data_as_dict(json_file)
general_indices = views_inverse_mapping(views_dict)

matches_names = []
value = 0
for models in tqdm(models_links):
    base_model = models[0]
    print(base_model)
    linked_models = models[1:]
    
    base_json_file = get_indices(base_model)
        
    _, base_views_dict, _, _ = get_sfm_data_as_dict(base_json_file)
    base_names = list(views_inverse_mapping(base_views_dict).keys())
    
    for i in range(len(base_names)-1):
        for j in range(i+1, len(base_names)):
            matches_names.append(base_names[i] + " " + base_names[j] + " %d" % value)
        
    for linked_model in linked_models:
        linked_json_file = './san_giorgio_image_listing/sfm_data_%s.json' % linked_model.split('-')[-1]
        
        if not os.path.exists(linked_json_file):
            linked_json_file = get_indices(linked_model)

        _, linked_views_dict, _, _ = get_sfm_data_as_dict(linked_json_file)
        linked_names = list(views_inverse_mapping(linked_views_dict).keys())
        
        for i in range(len(base_names)):
            for j in range(len(linked_names)):
                matches_names.append(base_names[i] + " " + linked_names[j] + " %d" % value) 
                
        value += 1
        
print("exporting matches")
        
matches_names_set = list(set(matches_names))
with open('san_giorgio_first_floor_matches.txt', 'w') as f:
    for match in matches_names_set:
        img1, img2, val = match.split()
        idx1 = general_indices.get(img1)
        idx2 = general_indices.get(img2)
        if idx1 != idx2:
            f.write('%d %d\n' % (min(idx1, idx2), max(idx1, idx2)))
        
with open('san_giorgio_first_floor_matrix.txt', 'w') as f:
    for match in matches_names_set:
        img1, img2, val = match.split()
        idx1 = general_indices.get(img1)
        idx2 = general_indices.get(img2)
        if idx1 != idx2:
            f.write('%d %d %s\n' % (min(idx1, idx2), max(idx1, idx2), val))