import numpy as np
import subprocess
import folium
from folium import IFrame
from folium.plugins import MarkerCluster
import pyproj
from pyproj import Proj, transform, Transformer
import os


# list of 3D models that have been georeferenced
models_list = open('gargantua_georef', 'r').read().split('\n')

# create a map centered on Piazza San Marco
m = folium.Map(location=[45.434285, 12.338791], zoom_start=14, max_zoom=50, tiles = 'cartodbpositron')

# points will have to be changed from Monte Mario 2 to Mercator
path_unix = '/media/gargantua/1000-plane/0000-sfm/'
transformer = Transformer.from_crs("EPSG:3004", "EPSG:4326")

mc = MarkerCluster()

for model in models_list:    
    if model != '':
        path_csv = path_unix + model[0:4] + "/" + model[4:8] + "/" + model + "/geodesy/" + model + "-epsg3004.csv"
        map_data = open(path_csv, 'r').read().strip().split('\n')[1:]
        images_path = '/media/gargantua/1000-plane/0000-sfm/' + model[0:4] + "/" + model[4:8] + "/" + model + "/images/"

        for marker in map_data:
            X,Y,filename = marker.split(',')

            if not os.path.isfile('./thumbnails/%s.jpg' % filename):
                os.system("convert %s%s.tif -thumbnail 300x300^ ./thumbnails/%s.jpg" % (images_path, filename, filename))

            # insert thumbnail in marker's popup
            html='<img src="../thumbnails/%s.jpg" width=500 height=350><b> %s </b>' % (filename, filename) 
            popup = folium.Popup(html, max_width=1000)
            lat, lon = transformer.transform(X,Y)
            mc.add_child(folium.Marker(location=[lat, lon], popup=popup))
            m.add_child(mc)



m.save('map/camera_poses.html')





