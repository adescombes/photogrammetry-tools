import click
from utils import least_squares_matching, get_sfm_data_as_dict, write_csv_from_dict

@click.command()
@click.option('--model_name', help='path to the model to be georeferenced')
@click.option('--epsg', help='EPSG in which the model must be displayed. the camera poses will be stored in a CSV file')

def vodom_to_csv(model_name, epsg):
    
    # get sfm data
    model_dir = "/".join([x for x in model_name.split("/")[:-1]])
    json_path =  model_dir + "/systems/omvg/sfm_data_bin.json"
    structure_dict, views_dict, extrinsics_dict, intrinsics = get_sfm_data_as_dict(json_path)
    
    # compute rigid transform
    F, R, t = least_squares_matching(model_dir +"/geodesy/homologous.dat")

    csv_path = model_dir + "/geodesy/" + model_name.split("/")[-1].replace('.ply','') + "-epsg" + epsg + ".csv"
    
    write_csv_from_dict(views_dict, extrinsics_dict, csv_path, F, R, t)
            
            
if __name__ == '__main__':
    vodom_to_csv()
