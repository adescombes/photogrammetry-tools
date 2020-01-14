"""
This algorithm is used to match the two set of points :
1. the source : a selection of points of the 3D model;
2. the target : the corresponding points selected on a cadastre map.
It is based on the least square matching of two 3D sets of points,
 explained here : http://nghiaho.com/?page_id=671.
"""

import numpy as np

def least_squares_matching(coor_model_file, coor_cadastre_file):

	# Get points selections

	n_pts = len(open(coor_model_file, 'r').read().split('\n')) -1

	source_pts = np.zeros((n_pts,3))
	i = 0
	for pts in open(coor_model_file, 'r').read().split('\n'):
		j = 0
		for pt in pts.split():
		    source_pts[i][j] = np.float(pt)
		    j += 1
		i += 1
		
	target_pts = np.zeros((n_pts,3))
	i = 0
	for pts in open(coor_cadastre_file, 'r').read().split('\n'):
		j = 0
		for pt in pts.split():
		    target_pts[i][j] = np.float(pt)
		    j += 1
		i += 1
		
	# scale factor

	F = []
	n = 0
	m = np.zeros((n_pts, n_pts))
	for i in range(n_pts-1):
		source_pt1 = source_pts[i]
		target_pt1 = target_pts[i]
		for j in range(i+1, n_pts):
		    source_pt2 = source_pts[j]
		    target_pt2 = target_pts[j]
		    f = (np.linalg.norm(target_pt1 - target_pt2) / np.linalg.norm(source_pt1 - source_pt2))
		    m[i,j] = f
		    F.append(f)
		    n += 1
		    
	F = np.sum(F) /n

	# apply scale factor to the source points
	scaled_source_pts = F*source_pts

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
	if np.linalg.det(R)<0:
		R[2,:] *= -1

	# translation
	t = np.subtract(centroid_source, np.matmul(R, centroid_target))

	return F,R,t

def transform(F,R,t,coor):
    return list(np.matmul(np.transpose(R), np.subtract(F * np.array(coor), t)))

