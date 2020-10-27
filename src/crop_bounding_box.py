from utils import read_ascii_ply, write_bin_ply, read_uv3, write_uv3
import numpy as np
import click
import re

@click.command()
@click.option('--model', help='path to the model to be cropped, in uv3 format')
@click.option('--bounding_box', help='path to the file containing the bounding box dimensions and center coordinates')
def crop(model, bounding_box):

    if model.split('.')[-1] is not 'uv3':
        print('The model must be converted to uv3 to be cropped\n%s' % model)
        break

    points_xyz, points_rgb = read_uv3(model)

    lines = open(bounding_box, 'r').readlines()
    bb_dim = re.sub("[^0-9]", " ", lines[0]).strip().split()
    bb_center = re.sub("[^0-9]", " ", lines[1]).strip().split()

    bb_dim_x = float('.'.join(bb_dim[:2]))
    bb_dim_y = float('.'.join(bb_dim[2:4]))
    bb_dim_z = float('.'.join(bb_dim[4:]))

    bb_center_x = float('.'.join(bb_center[:2]))
    bb_center_y = float('.'.join(bb_center[2:4]))
    bb_center_z = float('.'.join(bb_center[4:]))

    min_x = bb_center_x - 0.5 * bb_dim_x
    min_y = bb_center_y - 0.5 * bb_dim_y
    min_z = bb_center_z - 0.5 * bb_dim_z
    max_x = bb_center_x + 0.5 * bb_dim_x
    max_y = bb_center_y + 0.5 * bb_dim_y
    max_z = bb_center_z + 0.5 * bb_dim_z

    # from https://stackoverflow.com/questions/42352622/finding-points-within-a-bounding-box-with-numpy
    def bounding_box(points, min_x, min_y, min_z, max_x, max_y, max_z):
        """ Compute a bounding_box filter on the given points

        Parameters
        ----------                        
        points: (n,3) array
            The array containing all the points's coordinates. Expected format:
                array([
                    [x1,y1,z1],
                    ...,
                    [xn,yn,zn]])

        min_i, max_i: float
            The bounding box limits for each coordinate. If some limits are missing,
            the default values are -infinite for the min_i and infinite for the max_i.

        Returns
        -------
        bb_filter : boolean array
            The boolean mask indicating wherever a point should be keeped or not.
            The size of the boolean mask will be the same as the number of given points.

        """

        bound_x = np.logical_and(points[:, 0] > min_x, points[:, 0] < max_x)
        bound_y = np.logical_and(points[:, 1] > min_y, points[:, 1] < max_y)
        bound_z = np.logical_and(points[:, 2] > min_z, points[:, 2] < max_z)

        bb_filter = np.logical_and(np.logical_and(bound_x, bound_y), bound_z)

        return bb_filter

    print('-- selecting points... --')
    inside_box = bounding_box(points_xyz, min_x, min_y, min_z, max_x, max_y, max_z)

    points_inside_box = points_xyz[inside_box]
    rgb_inside_box = points_rgb[inside_box]

    file_out = model.replace('.uv3','-cropped.uv3')

    print('-- writing to file... --\n%s' % file_out)
    write_uv3(points_inside_box, rgb_inside_box, file_out)
    
if __name__ == '__main__':
    crop()