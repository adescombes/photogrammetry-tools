
"""
This program aims at transforming a 3D point cloud by matching it onto a set
of geographical coordinates, in order to display it in geographical information systems.
IN : - 3D model in .uv3 format, whose indicated path will be used to get the point selections for the least square fitting
	- chosen EPSG 
OUT : georeferenced 3D model in ply or uv3 format (depending on the format of the input file), in the chosen EPSG 
"""

import numpy as np
import json
import sys
import struct

sys.path.append('../share')
from least_squares_matching import least_squares_matching

file_in = sys.argv[1] # full path to file
version = '/'.join(file_in.split('/')[:-1])
format = file_in.split('.')[-1]
epsg = sys.argv[2]
coor_model_file = version + '/geodesy/points_model'
coor_cadastre_file = version + '/geodesy/points_cadastre_epsg' + epsg

F,R,t = least_squares_matching(coor_model_file,coor_cadastre_file)

file_out = file_in.replace('.', '-epsg%s.' % epsg)

if format == 'ply': # ply ascii format
    f_in = open(file_in, 'r').readlines()
    pt_idx = f_in.index('end_header\n')
    points = f_in[pt_idx+1:]

    with open(file_out, 'w') as f_out:
        for line in f_in[:pt_idx+1]:
            f_out.write("%s" %(line.replace('float', 'double')))
        for pt in points:
            colors = ' '.join(x for x in pt.split()[3:])
            camera_pose = [np.float(xx) for xx in pt.split()[:3]]
            coors = np.array(np.matmul(np.transpose(R), np.subtract(F * np.array(camera_pose), t)), dtype=np.float64)
            f_out.write(str(coors[0]) + " " + str(coors[1]) + " " + str(coors[2]) + " " + colors + "\n")

elif format == 'uv3': # uv3 binary format
    with open(file_in, 'rb') as f_in:
        with open(file_out, 'wb') as f_out:
            while True:
                byte = f_in.read(28)
                
                if not byte:
                    break
                    
                x,y,z,a,r,g,b = struct.unpack('<dddBBBB', byte)
                xx,yy,zz = np.matmul(np.transpose(R), np.subtract(F * np.array([x,y,z]), t))
                export = struct.pack('<dddBBBB', xx, yy, zz, a, r, g, b)
                f_out.write(export)

else:
    print('unknown format')
