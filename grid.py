# coding: utf-8

import numpy as np
import pandas as pd
from scipy import interpolate
import os
import shapefile


class Grid(object):
	def __init__(self, shp_file_path, region, density=100):
		"""
		建立网格对象， 以shp文件获取的 region 外包矩形为网格外边界
		:param shp_file_path:  str -> 要打开的 shapefile 文件
		:param region:  str or int -> 地区名 或 地区编码
						会检索 shp file infos 的所有 record 进行匹配， 因此，
						需保证此值唯一性， 否则将获取拥有此值的最后一个元素
		:param density:  float -> 网格密度， 单位：格/度
		"""
		self.region = region
		self.shp_file_path = shp_file_path
		self.density = density
		self.shp_file = shapefile.Reader(shp_file_path)
		for shape_record in self.shp_file.shapeRecords():
			if str(region) in shape_record.record:
				self.points = shape_record.shape.points
		# self.points = self.shp_file.shape().points
		
		self.lons, self.lats = zip(*self.points)
		self.min_lon = min(self.lons)
		self.max_lon = max(self.lons)
		self.min_lat = min(self.lats)
		self.max_lat = max(self.lats)
		self.grid_lon_num = (self.max_lon - self.min_lon) * density
		self.grid_lat_num = (self.max_lat - self.min_lat) * density
		self.grid = np.mgrid[
			self.min_lon:self.max_lon:complex(0, self.grid_lon_num),
			self.min_lat:self.max_lat:complex(0, self.grid_lat_num)
		]
	
	def grid_data(
		self, file, method='nearest',
		lon_column='经度', lat_column='纬度', value_column='值',
		**kwargs
	):
		"""
		根据已有原始数据插值建立空间网格模型， 并将各参数绑定到 Grid 对象中。
		:param file:  str -> 数据文件的路径，（CSV 文件）
		:param method:  str -> 插值方法，采用 scipy.interpolate.griddata() 方法进行计算。
		:param lon_column:  str -> 数据 经度列的字段名
		:param lat_column:  str -> 数据 纬度列的字段名
		:param value_column:  str -> 数据 数据值列的字段名
		:return:  grid -> 网格值， 同 scipy.interpolate.griddata() 方法
		"""
		if not os.path.exists(file):
			return None
		data_frame = pd.read_csv(file)
		self.ori_data_lons = np.array(data_frame.get(lon_column))
		self.ori_data_lats = np.array(data_frame.get(lat_column))
		self.ori_data_value = np.array(data_frame.get(value_column))
		data = interpolate.griddata(
			np.array([self.ori_data_lons, self.ori_data_lats]).T,
			self.ori_data_value, self.grid.T, method=method, **kwargs
		)
		self.data = data
		return data.T
		
		
if __name__ == '__main__':
	grid = Grid(1)
	grid_data = grid.grid_data(os.path.join('data', '0.csv'), method='cubic')
	t = np.array([*grid.grid, grid_data])
	print(grid.grid)
