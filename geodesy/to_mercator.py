"""
This program aims at changing the coordinates system of a 3D model, here from the system of the IN file to the Mercator system.
IN : georeferenced 3D model in a binary ply file.
OUT : same but coordinates changed to Mercator system.
To go from one system to the other, the pyproj library is used. Note that the altitude is not changed from the first system to the second.
"""

import pandas as pd
import numpy as np
import struct
import sys
import pyproj
from pyproj import Proj, transform, Transformer

file_in = sys.argv[1]
epsg1 = file_in.partition('epsg')[-1][:4]
epsg2 = 4326

file_out = file_in.replace(epsg1, '4326')
transformer = Transformer.from_crs(int(epsg1), epsg2)

with open(file_in, 'rb') as filein:
    with open(file_out, 'wb') as out:
        while True:
            byte = filein.read(28)
            
            if not byte:
                break
                
            x,y,z,t,r,g,b = struct.unpack('<dddBBBB', byte)
            xx,yy,zz = transformer.transform(x,y,z)
            xx_rad = xx * np.pi / 180
            yy_rad = yy * np.pi / 180
            export = struct.pack('<dddBBBB', yy_rad, xx_rad, zz, t, r, g, b)
            out.write(export)
