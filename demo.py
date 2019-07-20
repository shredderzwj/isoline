# coding: utf-8

import matplotlib.pyplot as plt
import os
import time
import numpy as np

import grid
import map
import utils


def draw_isoline(
		grid_shp_file=os.path.join('shp', '省界_region.shp'),
		grid_region='河南省',
		grid_data_file=os.path.join('data', 'hn.csv'),
		grid_density=500,
		grid_data_lon_column='经度',
		grid_data_lat_column='纬度',
		grid_data_value_column='值',
		method='cubic',
		map_projection='cyl',
		map_shp_file_region=os.path.join('shp', '市界_region.shp'),
		map_region=['郑州市'],
		map_shp_file_point=None,
		map_point=None,
		**kwargs
):
	t1 = time.time()
	print('创建网格...')
	grid_s = grid.Grid(grid_shp_file, grid_region, grid_density)
	grid_data = grid_s.grid_data(
		grid_data_file,
		method=method,
		lon_column=grid_data_lon_column,
		lat_column=grid_data_lat_column,
		value_column=grid_data_value_column,
	)
	t2 = time.time()
	print('完成创建网格！ -> %.3fs\n' % (t2 - t1))
	if not isinstance(map_region, list):
		map_region = [map_region]

	for region in map_region:
		print('获取绘图区域遮罩... - > %s' % region)
		t2_1 = time.time()
		map_s = map.Map(map_shp_file_region, region,
			right_blank=0.05, left_blank=0.05, upper_blank=0.05, lower_blank=0.05,
			projection=map_projection, **kwargs
		)
		grid_data_c = utils.mask_grid_data(grid_s.grid, grid_data, map_s.lons, map_s.lats)
		t3 = time.time()
		print('完成获取绘图区域遮罩！ -> %.3fs' % (t3 - t2_1))

		print('投影... - > %s' % region)
		x, y = map_s.map(*grid_data_c[0])
		x1, y1 = map_s.map(map_s.lons, map_s.lats)
		# if map_shp_file_point and map_point:
		# 	x2, y2 = map_s.map()
		t4 = time.time()
		print('完成投影！ -> %.3fs' % (t4 - t3))

		print('绘图... - > %s' % region)
		plt.figure(figsize=[12.8, 9])
		# plt.title(region, size=12)
		plt.rcParams['font.family'] = ['sans-serif']
		plt.rcParams['font.sans-serif'] = ['SimHei']

		map_s.map.contourf(x, y, grid_data_c[1], levels=6, alpha=0.5)
		map_s.map.colorbar(size="5%", pad='0.5%')
		map_s.map.plot(x1, y1, color='k', linewidth=4)
		CS = map_s.map.contour(x, y, grid_data_c[1], levels=6, linestyles='dashed')
		plt.clabel(CS, inline=True, fontsize=10, fmt='%2.0f', colors='k')
		# map_s.draw_scale(yoffset_times=0.01)
		# 绘制经纬度线
		map_s.draw_lon_lat_lines()
		# plt.scatter(*map_s.map(grid_s.ori_data_lons, grid_s.ori_data_lats))
		coor = map_s.draw_region_name(os.path.join('shp', '市_point.shp'), region)
		plt.text(*coor, ' %s' % region, fontsize=14)
		t5 = time.time()
		# plt.show()
		plt.savefig(os.path.join('img', '%s.png' % region), bbox_inches='tight')
		print('完成绘图！ -> %.3fs\n' % (t5 - t4))
	print('总耗时 -> %.3fs' % (t5 - t1))


if __name__ == '__main__':
	regions = [
		'郑州市',
		'开封市',
		'洛阳市',
		'信阳市',
		'驻马店市',
		'南阳市',
		'三门峡市',
		'周口市',
		'商丘市',
	]
	draw_isoline(
		grid_shp_file=os.path.join('shp', '省界_region.shp'),
		grid_region='河南省',
		grid_data_file=os.path.join('data', 'hn.csv'),
		grid_density=300,
		grid_data_lon_column='经度',
		grid_data_lat_column='纬度',
		grid_data_value_column='值',
		method='cubic',
		map_projection='merc',
		map_shp_file_region=os.path.join('shp', '市界_region.shp'),
		map_region=regions,
		map_shp_file_point=None,
		map_point=None,
	)

