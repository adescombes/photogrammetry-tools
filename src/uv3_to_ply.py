import pandas as pd
import numpy as np
import re
import sys
sys.path.append('/home/descombe/Desktop/photogrammetry-tools/src/utils.py')
from utils import read_uv3, write_bin_ply, write_ascii_ply, make_header
import click

@click.command()
@click.option('--file_in',help='full path to the model to be converted')
@click.option('--encoding',help='ascii or bin (little endian)')

def uv3_to_ply(file_in: str, encoding: str):
	points_xyz, points_rgb = read_uv3(file_in)
	file_out = file_in.replace('uv3','ply')
    
	if encoding == 'ascii':
		write_ascii_ply(points_xyz, points_rgb, file_out)
        
	elif encoding is 'ply':
		write_bin_ply(points_xyz, points_rgb, file_out)
        
	else:
		print('encoding must be ascii or bin')

if __name__ == '__main__':
	uv3_to_ply()
