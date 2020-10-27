import click
import os
from utils import least_squares_matching, get_sfm_data_as_dict, write_csv_from_dict

@click.command()
@click.option('--model', help='path to the model to be georeferenced')
@click.option('--points', help='path to the file containing the pairs of homologous points')
@click.option('--epsg', help='EPSG in which the model must be displayed. the camera poses will be stored in a CSV file')

def vodom_to_csv(model, points, epsg):
    
    # get sfm data
    model_dir = "/".join([x for x in model.split("/")[:-1]])
    json_path =  model_dir + "/omvg/sfm_data_bin.json"
    if not os.path.exists(json_path):
        json_path = model_dir + "/omvg/sfm_data.json"
        print("brigitte")
    structure_dict, views_dict, extrinsics_dict, intrinsics = get_sfm_data_as_dict(json_path)
    
    # compute rigid transform
    F, R, t = least_squares_matching(points)

    csv_path = model_dir + "/geodesy/" + model.split("/")[-1].replace('.ply','') + "-epsg" + epsg + ".csv"
    
    write_csv_from_dict(views_dict, extrinsics_dict, csv_path, F, R, t)
            
            
if __name__ == '__main__':
    vodom_to_csv()
