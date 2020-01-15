"""
This program aims at transforming a 3D point cloud by matching it onto a set
of geographical coordinates, in order to display it in geographical information systems.
IN : - 3D model in .uv3 format, whose indicated path will be used to get the point selections for the least square fitting
	- chosen EPSG 
OUT : georeferenced 3D model in .uv3 format, in the chosen EPSG 
"""

import numpy as np
import json
import sys
import struct

sys.path.append('../share')
from least_squares_matching import least_squares_matching

file_in = sys.argv[1] # full path to .uv3 file
version = '/'.join(file_in.split('/')[:-1])
epsg = sys.argv[2]
coor_model_file = version + '/geodesy/points_model'
coor_cadastre_file = version + '/geodesy/points_cadastre_epsg' + epsg

F,R,t = least_squares_matching(coor_model_file,coor_cadastre_file)

file_out = file_in.replace('.uv3', '-epsg%s.uv3' % epsg)
print(file_out)
print(file_in)
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


