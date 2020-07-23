import click
from utils import get_sfm_data_as_dict

@click.command()
@click.option('--json', help="full path to the json file")

def print_missing_images(json: str):
    structure_dict, views_dict, extrinsics_dict, intrinsics = get_sfm_data_as_dict(json)

    # get missing files (images that have not been used for the 3D reconstruction)
    if len(views_dict.keys()) > len(extrinsics_dict.keys()):
        for item in views_dict.keys():
            if item not in list(extrinsics_dict.keys()):
                print(views_dict.get(item)['ptr_wrapper']['data']['filename'].split('.')[0])

    else:
        print('there are no missing images')
        
if __name__ == '__main__':
    print_missing_images()