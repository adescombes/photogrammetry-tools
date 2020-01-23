import sys
import json
from glob import glob
import os
import numpy as np
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import re

SFM_MOUNT = sys.argv[1]
SFM_LISTING =  sys.argv[2]
SFM_MODEL = sys.argv[3]
SFM_GROUPS = sys.argv[4]
SFM_PFILE = sys.argv[5]

with open("/home/descombe/triplets/test.txt","w") as f1:
    f1.write("SFM_MOUNT " + SFM_MOUNT)
    f1.write("\nSFM_LISTING " + SFM_LISTING)
    f1.write("\nSFM_MODEL " + SFM_MODEL)
    f1.write("\nSFM_GROUPS " + SFM_GROUPS)
    f1.write("\nSFM_PFILE " + SFM_PFILE)
f1.close()

dict_links = {}
dict_properties = {}
dict_connections = {}

for model in open(SFM_GROUPS, 'r').read().split('\n'):
    if model is not '': # avoid empty strings
        model_name = model.split('-')[-1]
        # list to store the properties of each model : 
        # 1. the path to its sfm_data.json file, to get the images it is composed of 
        # 2. the path to its connections to other models
        properties = []

        # if sfm for this model has been computed : the model exists in 1000-sfm and the filename contains 5 '-'
        if len(re.split(r'([a-z])', model)[0].split('-')) == 5:

            # we store the path to the sfm_data.json file 
            sfm_data_path = SFM_MOUNT + '/' + model[0:4] + '/' + model[4:8] + '/' + model  + "/systems/omvg/sfm_data.json"
            properties.append(sfm_data_path)

            # we check if a .txt file exists in 0500-image to get the possible connections of the model
            connections_path = SFM_LISTING + '/' + '-'.join(model.split('-')[2:])[0:4] + '/' + '-'.join(model.split('-')[2:])[4:8]  +'/' + '-'.join(model.split('-')[2:]) + '.txt'

            if not os.path.exists(connections_path):
                print("No connections found for " + model_name)

            else:
                # if it exists we store it in the properties of the model
                properties.append(connections_path)

        # if sfm for this model has not been computed (only the 0500-image file is given as input, and this filename contains 3 '-')
        # we have to create the sfm_data.json file with openMVG_main_SfMInit_ImageListing and store it in the "group" folder 
        elif len(re.split(r'([a-z])', model)[0].split('-')) == 3:

            # path to the folder where the images are stored
            sfm_data_path_in = SFM_LISTING + "/" + model[0:4] + "/" + model[4:8] + "/" + model
            # path to the temporaty folder
            sfm_data_path_out = SFM_MOUNT + "/" + SFM_MODEL[0:4] + "/" + SFM_MODEL[4:8] + "/" + SFM_MODEL + "/systems/groups"

            os.system("openMVG_main_SfMInit_ImageListing -i %s -o %s" %(sfm_data_path_in, sfm_data_path_out))
            # rename the file accurately
            os.system("mv %s/sfm_data.json %s" %(sfm_data_path_out, (sfm_data_path_out + "/" + model_name + "-sfm_data.json")))

            # add the path to the json file to the properties
            properties.append(sfm_data_path_out + "/" + model_name + "-sfm_data.json")

            # we check if a .txt file exists in 0500-image to get the possible connections of the model
            connections_path = SFM_LISTING + '/' + '-'.join(model.split('-'))[0:4] + '/' + '-'.join(model.split('-'))[4:8]  +'/' + '-'.join(model.split('-')) + '.txt'
            if not os.path.exists(connections_path):
                print("No connections found for " + model_name)
            else:
                properties.append(connections_path)


        dict_properties.update({ model_name : properties })



# to update the connections in 0500-plane, we list all the connections of each model and copy it in a text file 
# for the newly created one, which encompasses them all. But first, check if the destination already exists

if not os.path.exists(SFM_LISTING + "/" + SFM_MODEL[16:20]):
    os.system("mkdir %s/%s" % (SFM_LISTING, SFM_MODEL[16:20]))
if not os.path.exists(SFM_LISTING + "/" + SFM_MODEL[16:20] + "/" + SFM_MODEL[20:24]):
    os.system("mkdir %s/%s/%s" % (SFM_LISTING, SFM_MODEL[16:20], SFM_MODEL[20:24]))
    
with open(SFM_LISTING + "/" + SFM_MODEL[16:20] + "/" + SFM_MODEL[20:24] + "/" + SFM_MODEL[16:] + ".txt", 'w') as f:

    for model, properties in dict_properties.items():
        connections = []

        # if properties has a size of 1, it only contains the path to the sfm_data.json file. 
        # if properties has a size of 2, it contains the path to sfm_data.json file and also the path to the .txt file of connections,
        # which will be used to add matches in the pairs-list.txt file
        if len(properties) > 1:

            for connection in open(properties[1], 'r').read().split('\n'):
                if connection is not '': # avoid empty strings
                    # first, write the connection in the new text file
                    f.write(connection + "\n")
                    # then, update the connections dict :
                    #if the connection listed in the .txt file is contained in the current group of models, add it to the dict
                    if connection.split()[-1] in [x.split('-')[-1] for x in dict_properties.keys()]:
                        # if this very connection is not yet in the list
                        if connection.split()[-1] not in connections:
                            connections.append(connection.split()[-1])

                dict_connections.update({model:connections})
f.close()


path_listing_in = SFM_LISTING + "/" + SFM_MODEL[16:20] + "/" + SFM_MODEL[20:24] + "/" + SFM_MODEL[16:]
path_listing_out =  SFM_MOUNT + "/" + SFM_MODEL[0:4] + "/" + SFM_MODEL[4:8] + "/" + SFM_MODEL + "/systems"

# create a sfm_data.json file for the bigger model and store it in the temporary folder.
# A folder has to be already present in the 0500-plane folder, and contain all the separate parts listed in the parts.txt file
#os.system("openMVG_main_SfMInit_ImageListing -i %s -o %s" % (path_listing_in, path_listing_out))



# create a dict of correspondances between names of the images and their index, based on the sfm_data.json of the bigger (general) model:
with open(path_listing_out + "/omvg/sfm_data.json") as json_data:
    data = json.load(json_data)
    
general_json = data['views']

general_filenames = []
general_id_poses = []
for item in general_json:
    filename = item['value']['ptr_wrapper']['data']['filename'].split('.')[0]
    general_filenames.append(filename)
    general_id_poses.append(item['value']['ptr_wrapper']['data']['id_pose'])

# dict : filename <-> index (from 0 to [nb of img - 1])
general_dict = dict(zip(general_filenames, general_id_poses))

# this list will contain all the matches for the big model
matches = []
# this dict will contain, for each model, the list of names of the images it is composed of 
dict_files_per_model = {}

# useful for visualizing the matrix of all separate models brought together :
# it will consist of a color code, each color and model correspond to a value in the matrix
labels = ['0']
labels_idx = 1

for model, properties in dict_properties.items():

    # get idx <-> filename with sfm_data.json
    with open(properties[0]) as json_data:
        data = json.load(json_data)
        
    views = data['views']
    filenames = []
    id_poses = []
    for view in views:
        filename = view['value']['ptr_wrapper']['data']['filename'].split('.')[0]
        id_pose = view['value']['ptr_wrapper']['data']['id_pose']
        filenames.append(filename)
        id_poses.append(id_pose)
    
    # create a dict of correspondances between index and names of each image, for each model : one dict per model
    # this dict will be used with the general_dict, to get the correspondency:
    # [index in local model] -> [filename in local model] -> [index in global model]
    dict_id_to_filename = dict(zip(id_poses, filenames))
    
    # udpate the dict by adding the listing of images of the current model
    dict_files_per_model.update({model : filenames})
    
    if 'groups' not in properties[0]: # if the model has already been computed, get the matches from its geometric matches
        svg_file = properties[0].replace("/sfm_data.json", "/matches/GeometricAdjacencyMatrix.svg")
        for line in open(svg_file, 'r').read().split('\n'):
            if "<rect" in line:
                x = ( np.float(line.split('"')[1]) / 5 )
                y = ( np.float(line.split('"')[3]) / 5 )
                filename_x = dict_id_to_filename.get(x)
                filename_y = dict_id_to_filename.get(y)
                # avoid Nulls in the list of matches
                if general_dict.get(filename_y) is not None:
                    if general_dict.get(filename_x) is not None:
                        if general_dict.get(filename_x) is not general_dict.get(filename_y):
                            matches.append([general_dict.get(filename_y), general_dict.get(filename_x), labels_idx])
                    
    else:
        for i in range(len(filenames)-1):
            filename_x = filenames[i]
            for j in range(i, len(filenames)):
                filename_y = filenames[j]
                if general_dict.get(filename_y) is not None:
                    if general_dict.get(filename_x) is not None:
                        if general_dict.get(filename_x) is not general_dict.get(filename_y):
                            matches.append([general_dict.get(filename_x), general_dict.get(filename_y), labels_idx])

    labels_idx += 1
    labels.append(model)


# connect models with each other, according to their respective connections

labels.append('links')

for model, connections in dict_connections.items():
    # if the model actually has connections -> this list is not empty
    if len(connections) > 0:
        for connection in connections:
            filenames1 = dict_files_per_model.get(model)
            filenames2 = dict_files_per_model.get(connection)
            for f1 in filenames1:
                for f2 in filenames2:
                    idx1 = general_dict.get(f1)
                    idx2 = general_dict.get(f2)
                    if idx1 is not None:
                        if idx2 is not None:
                            if idx1 < idx2:
                                matches.append([idx1, idx2, labels_idx])
                            elif idx1 > idx2:
                                matches.append([idx2, idx1, labels_idx])


with open(SFM_PFILE, 'w') as f:
    for pair in matches:
        f.write("%d %d\n" % (pair[0], pair[1]))

# plot matrix
plt.rcParams["figure.figsize"] = (15,15)
min_ = min(general_dict.values()) 
max_ = max(general_dict.values()) 
dim = max_ - min_ + 1

m = np.zeros((dim, dim))

for pair in matches:
    i = pair[0]-min_
    j = pair[1]-min_
    m[i,j] = pair[2]

plt.matshow(m, cmap=plt.cm.get_cmap('tab20_r',len(labels)))
cbar = plt.colorbar(ticks=range(len(labels)))
cbar.ax.set_yticklabels(labels, fontsize=18)
plt.xticks(np.arange(0, dim, step=50))

plt.savefig(path_listing_out + '/groups/matches.png', bbox_inches='tight', dpi = 400)

