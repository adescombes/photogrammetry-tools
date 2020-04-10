
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
import click

sys.path.append('../share')
from least_squares_matching import least_squares_matching

@click.command()
@click.option('--file', help='path to ply (ascii) or uv3 (binary) format')
@click.option('--source', help='List of selected points on the source point cloud')
@click.option('--target', help='List of selected points on the target point cloud')
@click.option('--epsg', default=None, help='SRID of the spatial coordinate system of the target point cloud')

file_format = file.split('.')[-1]

F,R,t = least_squares_matching(source,target)

if epsg is not None: # the transformation is a geolocalisation
    file_out = file.replace('.', '-epsg%s.' % epsg)
else: # the transformation is for point cloud matching
    file_out = file.replace('.', '-matched.')
    
if file_format == 'ply': # ply ASCII format
    f_in = open(file, 'r').readlines()
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

elif file_format == 'uv3': # uv3 binary format
    with open(file, 'rb') as f_in:
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