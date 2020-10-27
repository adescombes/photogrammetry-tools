# photogrammetry-tools

Tools for analyzing and georeferencing 3D models. The necessary files are obtained with an openMVG pipeline and stored on the \'gargantua\' share.

### georeferencing tool
This python script can be used to transform the coordinates of a model from its arbitrary referential to a chosen cartesian geographical referential. The file containing the homologous points, necessary for computing a rigid transform from one 3D referential to the other, is of the following format:
```
source_point_1_x source_point_1_y source_point_1_z target_point_1_x target_point_1_y target_point_1_z
source_point_2_x source_point_2_y source_point_2_z target_point_2_x target_point_2_y target_point_2_z
...
```
Ideally the target points are selected on a cadaster map of the chosen referential.

```
python vodom_to_csv.py --model <path-to-the-model-to-be-georeferenced>
                          --points <path-to-the-homologous-points>
                          --epsg <epsg-code-of-the-chosen-referential>

```

### missing pictures tool
When a model is computed, it often happens that all input images do not appear on the final model. To get the list of the names of missing images, a simple python script can be used as following:

```
python get_missing_files.py --json <path-to-the-sfm-data-file>
```

