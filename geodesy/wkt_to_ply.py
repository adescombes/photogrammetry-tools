"""
This program can be used to transform a georeferenced polygon or set of points (i.e. cadastre map) into a 2D cloud point.
The goal is to display it at the same time as a georeferenced 3D cloud of points and check the presicion of 
the positionning of the latter.
IN : CSV file containing the geographical coordinates in WKT (well-known text format, commonly used in QGIS exports)
OUT : PLY file (can be opened with Meshlab or CloudCompare). The height (z-coordinate) of the points is arbitrarily set to 0.
"""

import sys
import pandas as pd
import numpy as np

path = sys.argv[1] # full path to .csv file

wkt = pd.read_csv(path, header=0, usecols = ['WKT'])

if 'POINT' in wkt['WKT'][0]:
    geometry = wkt['WKT'].apply(lambda x : x.replace('POINT ', '').replace('(', '').replace(')', '').strip())
elif 'POLYGON' in wkt['WKT'][0]:
    geometry = wkt['WKT'].apply(lambda x : x.replace('POLYGON ', '').replace('(', '').replace(')', '').strip())

pt_list = []
for coors in geometry:
    for coor in coors.split(','):
        x = np.float(coor.split()[0])
        y = np.float(coor.split()[1])
        
        pt_list.append(str(x) +" "+str(y))
        
header = ['ply',
 'format ascii 1.0',
 'element vertex %s' % len(pt_list),
 'property double x',
 'property double y',
 'property double z',
 'property uchar red',
 'property uchar green',
 'property uchar blue',
 'end_header']

z = 0 # can be modified but the same height will be assigned to all points

path_out = path.replace('.csv', '.ply')
with open(path_out, 'w') as file:
    for line in header:
        file.write("%s\n" % line)
    for pt in pt_list:
        file.write("%s %d 126 126 126\n" % (pt, z)) 
