# coding: utf-8

import shapefile
import os
from mpl_toolkits.basemap import Basemap
import math
import numpy as np


class Map(object):
	def __init__(
			self, shp_file_path, region,
			left_blank=0.1, right_blank=0.1, upper_blank=0.1, lower_blank=0.1,
			projection='cyl',
			**kwargs,
	):
		"""
		创建地图， 用于绘图的空间，将生成的 Basemap 对象 map 以及各参数绑定到 Map 类上面
		:param shp_file_path:  str -> 要打开的 shapefile 文件
		:param region:  str or int -> 地区名 或 地区编码
						会检索 shp file infos 的所有 record 进行匹配， 因此，
						需保证此值唯一性， 否则将获取拥有此值的最后一个元素
		:param left_blank:  float -> 左空白，占整个绘图区域宽度的比例
		:param right_blank:  float -> 右空白，占整个绘图区域宽度的比例
		:param upper_blank:  float -> 上空白，占整个绘图区域宽度的比例
		:param lower_blank:  float -> 下空白，占整个绘图区域宽度的比例
		:param projection:  str -> 地图成图投影方式 同 Basemap 类
		:param kwargs:  创建 Basemap 对象实例的其他参数
		"""
		self.shp_file_path = shp_file_path
		self.region = region
		self.right_blank = right_blank
		self.left_blank = left_blank
		self.upper_blank = upper_blank
		self.lower_blank = lower_blank
		self.max_lon = 180
		self.min_lon = 0
		self.max_lat = 90
		self.min_lat = -90
		if not os.path.exists(shp_file_path):
			pass
		else:
			self.shp_file = shapefile.Reader(shp_file_path)
			for shape_record in self.shp_file.shapeRecords():
				if str(region) in shape_record.record:
					points = shape_record.shape.points
					self.lons, self.lats = zip(*points)
					self.max_lon = max(self.lons)
					self.max_lat = max(self.lats)
					self.min_lon = min(self.lons)
					self.min_lat = min(self.lats)
		axes_x_length = (self.max_lon - self.min_lon) / (1 - (left_blank + right_blank))
		axes_y_length = (self.max_lat - self.min_lat) / (1 - (upper_blank + lower_blank))
		self.llcrnrlon = self.min_lon - axes_x_length * left_blank
		self.llcrnrlat = self.min_lat - axes_y_length * lower_blank
		self.urcrnrlon = self.max_lon + axes_x_length * right_blank
		self.urcrnrlat = self.max_lat + axes_y_length * upper_blank
		self.lon_0 = (self.min_lon + self.max_lon) / 2
		self.lat_0 = (self.min_lat + self.max_lat) / 2
		self.paint_area = {
			'lon_0': self.lon_0,
			'lat_0': self.lat_0,
			'llcrnrlon': self.llcrnrlon,
			'llcrnrlat': self.llcrnrlat,
			'urcrnrlon': self.urcrnrlon,
			'urcrnrlat': self.urcrnrlat,
		}
		self.map = Basemap(**self.paint_area, projection=projection, **kwargs)
	
	def draw_scale(self, length_offset_times=0.25, yoffset_times=None, barstyle='fancy', **kwargs):
		"""
		绘制比例尺， 非等距投影无法绘制比例尺，建议绘制经纬网
		:param length_offset_times:  float -> 长度比例
		:param yoffset_times:  float -> 长宽比, 默认0.02
		:param kwargs:  float -> 其他参数
		:param barstyle:  str -> 比例尺样式
		:return: 无返回值
		"""
		lon = (self.max_lon + self.min_lon) / 2
		lat = (self.min_lat + self.llcrnrlat) / 2
		lon_0 = self.lon_0
		lat_0 = self.lat_0
		l_x, l_y = self.map(self.llcrnrlon, self.llcrnrlat)
		u_x, u_y = self.map(self.urcrnrlon, self.urcrnrlat)
		for _x in [10 ** i for i in range(-3, 9)]:
			real_length = (u_x - l_x) / 1000 * length_offset_times
			if (real_length > _x / 10) and (real_length < _x):
				length = math.ceil((u_x - l_x) / 1000 * length_offset_times / (_x / 10)) * (_x / 10)
		if not yoffset_times is None:
			yoffset = (u_y - l_y) * yoffset_times
		else:
			yoffset = None
		self.map.drawmapscale(lon, lat, lon_0, lat_0, length, yoffset=yoffset, barstyle=barstyle, **kwargs)
	
	def draw_colorbar(self):
		pass

	def draw_lon_lat_lines(self, lon_line_num=7, lat_line_num=7, ratio=True):
		lon_width = self.urcrnrlon - self.llcrnrlon
		lat_width = self.urcrnrlat - self.llcrnrlat
		if ratio == True:
			if lon_width > lat_width:
				lat_line_num = int(lon_line_num * lat_width / lon_width) + 1
			else:
				lon_line_num = int(lat_line_num * lon_width / lat_width) + 1
		meridians = np.linspace(self.min_lon, self.max_lon, lon_line_num)
		parallels = np.linspace(self.min_lat, self.max_lat, lat_line_num)
		# 绘制经度线
		self.map.drawmeridians(meridians, labels=[0, 0, 1, 1], fontsize=10, fmt='%.2f', dashes=[1, 4], color='gray')
		# 绘制纬度线
		self.map.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10, fmt='%.2f', dashes=[1, 4], color='gray')
		return [meridians, parallels]

	def draw_region_name(self, shp_file_name=None, region_name=None):
		shp = shapefile.Reader(shp_file_name)
		for shape_record in shp.shapeRecords():
			if region_name in shape_record.record:
				lon, lat = shape_record.shape.points[0]
		x, y = self.map(lon, lat)
		self.map.scatter(x, y, s=100, color='r', marker='*')
		return [x, y]


if __name__ == '__main__':
	shp = shapefile.Reader(os.path.join('shp', '县界_region.shp'))
	for shape_record in shp.shapeRecords():
		if '中牟县' in shape_record.record:
			print(shape_record.record)
			print(shape_record.shape.points)
