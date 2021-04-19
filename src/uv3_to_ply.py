import pandas as pd
import numpy as np
import os
import sys
import struct
sys.path.append('/home/descombe/Desktop/photogrammetry-tools/src/utils.py')
from utils import make_header
import click

@click.command()
@click.option('--file_in',help='full path to the model to be converted')
def uv3_to_ply(file_in: str):
    
    file_out = file_in.replace('uv3','ply')

        
    file_size = os.path.getsize(file_in)

    if file_size % 28 != 0:
        print('The number of points cannot be determined, conversion to binary ply stopped.')

    else:
        n_points = int(file_size / 28) - 392
        header = make_header(n_points, 'bin')
        n = 0
        with open(file_out, 'wb') as f_out:
            f_out.write(header.encode('ascii'))
    
            with open(file_in, 'rb') as f_in:

                    while True:
                        byte = f_in.read(28)

                        if not byte:
                            break

                        x,y,z,t,r,g,b = struct.unpack('<dddBBBB', byte)
                        if [r,g,b] != [0,255,0]:
                            #n+=1
                            export = struct.pack('<dddBBB',x,y,z,r,g,b)
                            f_out.write(export)

                    f_in.close()

            f_out.close()
            print(n)
            
            
if __name__ == '__main__':
    uv3_to_ply()
