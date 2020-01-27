import numpy as np
import sys

SFM_MOUNT = '/media/gargantua/1000-plane/0000-sfm/'

# input : svg file ("Geometric" or "Putative" Adjacency Matrix) for a given model
# output : list of matches
def read_matrix(model, matrix): 
    matches = []
    svg_file = SFM_MOUNT + "/" + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/matches/" + matrix + "AdjacencyMatrix.svg"
    for line in open(svg_file, 'r').read().split('\n'):
        if "<rect" in line:
            x = ( np.float(line.split('"')[1]) / 5 )
            y = ( np.float(line.split('"')[3]) / 5 )
            matches.append(sorted([int(x),int(y)]))
    return matches

# input : list of matches
# output : matrix to display/save
def plot_matrix(matches):
    m = np.zeros((max(max(matches)) + 1, max(max(matches)) + 1))

    for pair in matches:
        i = pair[0]
        j = pair[1]
        m[i,j] = 1
    return m

