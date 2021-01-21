import numpy as np
import struct
import json 
import pandas as pd

def least_squares_matching(file_in):
    """
    algo found at http://nghiaho.com/?page_id=671.
    """
    # Get points selections
    source_pts = np.loadtxt(file_in, usecols=[0,1,2])
    target_pts = np.loadtxt(file_in, usecols=[3,4,5])


    # scale factor
    F = []
    n = 0
    m = np.zeros((len(source_pts), len(source_pts)))
    for i in range(len(source_pts) - 1):
        source_pt1 = source_pts[i]
        target_pt1 = target_pts[i]
        for j in range(i + 1, len(source_pts)):
            source_pt2 = source_pts[j]
            target_pt2 = target_pts[j]
            f = ( np.linalg.norm( target_pt1 - target_pt2 ) / np.linalg.norm( source_pt1 - source_pt2 ) )
            m[i,j] = f
            F.append(f)
            n += 1

    F = np.sum(F) / n

    # apply scale factor to the source points
    scaled_source_pts = F * source_pts

    # centroids
    centroid_source = np.mean(scaled_source_pts, axis=0)
    centroid_target = np.mean(target_pts, axis=0)

    # Familiar covariance matrix
    H = np.zeros((3,3))
    for i in range(len(source_pts)):
        h_source = np.subtract(scaled_source_pts[i], centroid_source)
        h_target = np.subtract(target_pts[i], centroid_target)
        M = np.outer(h_target, h_source)
        H = np.add(H, M)

    # SVD decomposition
    U, S, V = np.linalg.svd(H)

    # Rotation matrix
    R = np.matmul(np.transpose(V), np.transpose(U))
    #if np.linalg.det(R) < 0:
    #    R[2,:] *= -1

    # translation
    t = np.subtract( centroid_source, np.matmul( R, centroid_target ))

    return F, R, t


"""------ Read and write -------"""

def make_header(nb_points: int, file_format:str):
    assert file_format in ["ascii", "binary", "bin"], "Unknown export format"
    if file_format is "binary" or "bin":
        file_format = "binary_little_endian"

    header = 'ply\nformat %s 1.0\nelement vertex %d\nproperty float64 x\nproperty float64 y\nproperty float64 z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n' %(file_format, nb_points)
    
    return header

def read_ascii_ply(file_path_in: str):
    f = open(file_path_in, 'r').readlines()
    pt_idx = f.index('end_header\n')
    points_xyz = np.loadtxt(file_path_in, skiprows=pt_idx+1, usecols=(0,1,2))
    points_rgb = np.loadtxt(file_path_in, skiprows=pt_idx+1, usecols=(3,4,5), dtype=int)
    return points_xyz, points_rgb


def read_wkt(file_path_in: str):
    """
    useful for reading csv files in which one column contains a geometry written in wkt (well-known-text) format.
    The z-dimension is added, 0 by default
    """
    wkt = pd.read_csv(file_path_in, header=0, usecols = ['WKT'])

    if 'POINT' in wkt['WKT'][0]:
        geometry = wkt['WKT'].apply(lambda x : x.replace('POINT ', '').replace('(', '').replace(')', '').strip())
    elif 'POLYGON' in wkt['WKT'][0]:
        geometry = wkt['WKT'].apply(lambda x : x.replace('POLYGON ', '').replace('(', '').replace(')', '').strip())
    elif 'MULTILINESTRING' in wkt['WKT'][0]:
        geometry = wkt['WKT'].apply(lambda x : x.replace('MULTILINESTRING ', '').replace('(', '').replace(')', '').strip())


    points_xyz = []
    for coors in geometry:
        for coor in coors.split(','):
            x = np.float(coor.split()[0])
            y = np.float(coor.split()[1])
            points_xyz.append([x,y,0])
            
    return points_xyz

def read_uv3(file_path_in: str):
    points_xyz = []
    points_rgb = []
    with open(file_path_in, 'rb') as f:
        while True:
            byte = f.read(28)
            if not byte:
                break
            x,y,z,t,r,g,b = struct.unpack('<dddBBBB', byte)
            points_xyz.append([x,y,z])
            points_rgb.append([r,g,b])
    f.close()
    return points_xyz, points_rgb

            
def write_ascii_ply(xyz_transf: list, 
                    points_rgb: list, 
                    file_path_out: str):
    header = make_header(len(xyz_transf), 'ascii')
    with open(file_path_out, 'w') as f:
        for line in header:
            f.write("%s" % line)
        for i in range(len(xyz_transf)):
            #xyz_transf = np.array(np.matmul(np.transpose(R), np.subtract(F * np.array(points_xyz[i]), t)), dtype=np.float64)
            for coor in xyz_transf:
                f.write(str(coor) + " ")
            for color in points_rgb[i]:
                f.write(str(color) + " ")
            f.write('\n')
            
def write_bin_ply(points_xyz, points_rgb, file_path_out):
    header = make_header(len(points_xyz), 'bin')
    
    with open(file_path_out, 'wb') as f:
        f.write(header.encode('ascii'))
        
        for i in range(len(points_xyz)):
            #xyz_transf = np.array(np.matmul(np.transpose(R), np.subtract(F * np.array(points_xyz[i]), t)), dtype=np.float64)
            export = struct.pack('<dddBBB',points_xyz[i][0], points_xyz[i][1], points_xyz[i][2], points_rgb[i][0], points_rgb[i][1], points_rgb[i][2])
            f.write(export)
            
def write_uv3(xyz_transf, points_rgb, file_path_out):
    with open(file_path_out, 'wb') as f:
        for i in range(len(xyz_transf)):
            x,y,z = xyz_transf[i]
            r,g,b = points_rgb[i]
            export = struct.pack('<dddBBBB', x,y,z,1,r,g,b)
            f.write(export)
            
            
def write_csv_from_list(xyz_transf, points_rgb, file_path_out):
    """
    only exports the camera poses, for georeferencing purposes
    """
    vodom_idx = points_rgb.tolist().index([0, 255, 0])
    points_poses = xyz_transf[vodom_idx:]
    with open(file_path_out, 'w') as f_out:
        f_out.write('X,Y,Z\n')
        for point in points_poses:
            f_out.write('%f,%f,%f\n' %(point[0], point[1], point[2]))
        
        
def write_csv_from_dict(views_dict, extrinsics_dict, file_path_out, F, R, t):
    """
    only exports the camera poses, for georeferencing purposes
    """ 
    with open(file_path_out, 'w') as f_out:
        f_out.write('X,Y,Z,filename\n')
        for key, value in views_dict.items():
            if extrinsics_dict.get(key) is not None: # otherwise the image has not been used
                filename = value['ptr_wrapper']['data']['filename']
                coors = np.array(extrinsics_dict.get(key)['center'])
                coors_transf = np.array(np.matmul(np.transpose(R), np.subtract(F * np.array(coors), t)), dtype=np.float64)
                f_out.write('%f,%f,%f,%s\n' %(coors_transf[0], coors_transf[1], coors_transf[2], filename))

        
"""--- Read SfM data ---"""


def _convert_list_to_dict(data_list): # -> this exists already in point_labelling
    data_dict = dict()
    for element in data_list:
        assert element['key'] not in data_dict.keys(), "Key entry already exists"
        data_dict.update({element['key']: element['value']})
    return data_dict


def get_sfm_data_as_dict(sfm_json_filename):
    """
    Read sfm data json file, and transforms it into dictionary
    """
    with open(sfm_json_filename, 'r') as fp:
        sfm_data = json.load(fp)

    views = sfm_data['views']
    structure = sfm_data['structure']
    extrinsics = sfm_data['extrinsics']
    intrinsics = sfm_data['intrinsics']

    updated_structure = list()
    for el in structure:
        el['value']['observations'] = _convert_list_to_dict(el['value']['observations'])
        updated_structure.append(el)

    structure_dict = _convert_list_to_dict(updated_structure)
    views_dict = _convert_list_to_dict(views)
    extrinsics_dict = _convert_list_to_dict(extrinsics)

    # Assert no data was lost
    id_points = [d['key'] for d in structure]
    assert len(structure_dict.keys()) == len(id_points), \
        "Conversion of 'structure' into dictionary may have lost data. \n Interrupting."
    assert len(structure_dict.keys()) == len(np.unique(id_points)), \
        "There are multiple entries for the same id point. \n Interrupting."

    return structure_dict, views_dict, extrinsics_dict, intrinsics



""" --- Read Adjacency matrices --- """

# input : svg file ("Geometric" or "Putative" Adjacency Matrix) for a given model
# output : list of matches
def read_matrix(model, matrix): 
    matches = []
    svg_file = '/media/gargantua/1000-plane/0000-sfm/' + model[0:4] + "/" + model[4:8] + "/" + model + "/systems/omvg/matches/" + matrix + "AdjacencyMatrix.svg"
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



    
