import matplotlib.pyplot as plt
import os
import time
import numpy as np
import shapefile

import grid
import map
import utils


def get_border(shp_file, filter):
    shp = shapefile.Reader(shp_file)
    regions_points = []
    for shape_record in shp.shapeRecords():
            if filter in shape_record.record[2]:
                print(shape_record.record)
                # print(shape_record.shape.points)
                regions_points.append(
                    {
                        'points': shape_record.shape.points,
                        'name': shape_record.record[0],
                        'id': shape_record.record[2],
                    }
                )
    return regions_points


def get_point(shp_file, filter):
    shp = shapefile.Reader(shp_file)
    for shape_record in shp.shapeRecords():
            if filter in shape_record.record:
                print(shape_record.record)
                # print(shape_record.shape.points)
                return shape_record.shape.points[0]


if __name__ == "__main__":
    map_shp_file = os.path.join('shp', '市界_region.shp')
    map_region = '新乡市'
    
    draw_map = map.Map(map_shp_file, map_region,
			right_blank=0.05, left_blank=0.05, upper_blank=0.05, lower_blank=0.05,
			projection='cyl')

    plt.figure(figsize=[29.7, 21])        
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']

    shp = shapefile.Reader('shp\\市界_region.shp')
    for info in shp.shapeRecords():
        if '新乡市' in info.record:
            points1 = info.shape.points
    plt.fill(*draw_map.map(*zip(*points1)), color='#EDEAE1')

    shp_file = os.path.join('shp', '县界_region.shp')
    shp_file1 = os.path.join('shp', '县_point.shp')
    regions_info = get_border(shp_file, '4107')
    for info in regions_info:
        name = info.get('name')
        points = info.get('points')
        lons, lats = draw_map.map(*zip(*points))
        point = get_point(shp_file1, name)
        draw_map.map.plot(lons, lats, color='#aaaaaa', linewidth=1)
        if not (name == '卫滨区' or name == '红旗区'):
            draw_map.map.scatter(*point,color='#E56200', s=50)
            plt.text(*point, ' %s' % name, fontsize=9)
    point1 = get_point('shp\\市_point.shp', '新乡市')
    plt.scatter(*point1, s=100, color='r', marker='*')
    plt.text(*point1, '  新乡市', fontsize=12)
    draw_map.map.plot(*draw_map.map(*zip(*points1)), color='#555555', linewidth=10)
    plt.savefig('新乡市.png', bbox_inches='tight')
    plt.show()