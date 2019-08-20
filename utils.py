# coding: utf-8

import numpy as np
import random
import os
import time

import grid


def mask_grid_data(mgrid, grid_data, ax, ay):
	"""
	过滤网格数据至指定封闭图形区域内部，将区域外的 griddata值设置为 np.nan 以达到屏蔽的效果。
	:param mgrid:  np.mgrid Type -> 整个网格
	:param grid_data:  scipy.interpolate.griddata Type -> 整个网格数据
	:param ax:  list, tuple or array etc. Type -> 封闭区域 x坐标
	:param ay:  list, tuple or array etc. Type -> 封闭区域 y坐标
	:return:  list -> index=0, np.mgrid Type 过滤后的网格； index=1, scipy.interpolate.griddata Type 过滤后的网格数据
	"""
	# 首先将网格缩小至多边形外包的矩形大小
	max_x = np.max(ax)
	min_x = np.min(ax)
	max_y = np.max(ay)
	min_y = np.min(ay)
	mask = ((mgrid[0] > max_x) | (mgrid[0] < min_x)) | ((mgrid[1] > max_y) | (mgrid[1] < min_y))
	for row in range(len(mask)):
		mgrid_convert_lat = mgrid[1][row][~mask[row]]
		lat_num = len(mgrid_convert_lat)
		if lat_num:
			break
	all_num = len(grid_data[~mask])
	lon_num = int(all_num / lat_num)
	grid_data_convert = grid_data[~mask].reshape(lon_num, lat_num)
	mgrid_convert_lon = mgrid[0][~mask].reshape(lon_num, lat_num)
	mgrid_convert_lat = mgrid[1][~mask].reshape(lon_num, lat_num)
	mgrid_convert = np.array([mgrid_convert_lon, mgrid_convert_lat])
	# 逐行扫描，获得需要屏蔽绘图的多边形外面的部分网格。
	mask_shape = []
	for col in range(len(mgrid_convert[1][0])):
		# 直线方程参数
		c = - mgrid_convert[1][0][col]
		# 获取网格每行所在直线Li与多边形所有交点 jds。
		# 从绘图区域的最左边开始，遇到一个交点，此后的网格点将进行一次 内/外 的转换。
		# 位于直线Li上面并且是 V或倒V 形的交点，由于其对 内/外 转换无影响，故忽略。
		jds = []
		for i in range(len(ax) - 1):
			tmpf1 = ay[i] + c
			tmpf2 = ay[i + 1] + c
			ji = tmpf1 * tmpf2
			if ji < 0:
				y = -c
				x = (y - ay[i])*(ax[i + 1] - ax[i]) / (ay[i + 1] - ay[i]) + ax[i]
				jds.append([x, y])
			elif ji == 0:
				if (ay[i - 1] + c) * (ay[i + 1] + c) < 0:
					y = -c
					x = (y - ay[i]) * (ax[i + 1] - ax[i]) / (ay[i + 1] - ay[i]) + ax[i]
					jds.append([x, y])
		if jds:
			jds.sort()
		mask_tmp = []
		for i in range(len(jds)):
			if i == 0:
				mask_tmp.append(((mgrid_convert[0] <= jds[i][0]) & (mgrid_convert[1] == jds[i][1])).T[col])
			elif i == len(jds) - 1:
				mask_tmp.append(((mgrid_convert[0] >= jds[i][0]) & (mgrid_convert[1] == jds[i][1])).T[col])
			elif np.mod(i, 2) == 0:
				mask_tmp.append(((mgrid_convert[0] >= jds[i - 1][0]) & (mgrid_convert[0] <= jds[i][0]) & (mgrid_convert[1] == jds[i][1])).T[col])
			else:
				mask_tmp.append((mgrid_convert[0] <= -100000000).T[0])
		mask_ = (mgrid_convert[0] <= -100000000).T[0]
		for _mask in mask_tmp:
			mask_ = mask_ | _mask
		mask_shape.append(mask_)
	grid_data_convert[np.array(mask_shape).T] = np.nan
	return [mgrid_convert, grid_data_convert]


def is_in_area(x, y, ax, ay):
	"""
	判断一点是否位于指定封闭多边形内部
	:param x:  float -> 点的x坐标
	:param y:  float -> 点的y坐标
	:param ax:  list, tuple or array etc. Type -> 多边形 x坐标列表
	:param ay:  list, tuple or array etc. Type -> 多边形 y坐标列表
	:return:  bool -> True 在内部； False 在外部； None 在边界上。
	"""
	# 保证多边形的顶点不位于射线上
	while True:
		# 假定射线所在直线方程 ax + by + c = 0; (x, y) 为端点， (xp, yp)为方向
		xp = x + random.uniform(1, 100)
		yp = random.uniform(1, 100) * max(ay)
		# a, b, c 为假定射线所在的方程  参数
		a = yp - y
		b = x - xp
		c = xp * y - x * yp
		j = 0
		for i in range(len(ax)):
			if abs(a * ax[i] + b * ay[i] + c) < 1e-30:
				j += 1
		if j == 0:
			break
	# 判断射线与各个边的交点个数
	jd = 0
	for i in range(len(ax) - 1):
		tmpf1 = a * ax[i] + b * ay[i] + c
		tmpf2 = a * ax[i + 1] + b * ay[i + 1] + c
		tmpa = np.arccos(
			((ax[i] - x) * (xp - x) + (ay[i] - y) * (yp - y)) / np.sqrt((ax[i] - x) ** 2 + (ay[i] - y) ** 2) / np.sqrt(
				(xp - x) ** 2 + (yp - y) ** 2))
		tmpb = np.arccos(((ax[i + 1] - x) * (xp - x) + (ay[i + 1] - y) * (yp - y)) / np.sqrt(
			(ax[i + 1] - x) ** 2 + (ay[i + 1] - y) ** 2) / np.sqrt((xp - x) ** 2 + (yp - y) ** 2))
		if (tmpf1 * tmpf2 < 0) and (tmpa + tmpb - np.pi < 0):
			jd += 1
		if tmpf1 * tmpf2 == 0:
			return None
	# 如果交点数为奇数，则位于内部；如果为偶数，位于外部。
	if np.mod(jd, 2) == 0:
		return False
	else:
		return True


if __name__ == '__main__':
	grid_s = grid.Grid(
		shp_file_path=os.path.join('shp', '省界_region.shp'),
		region='河南省',
		density=100,
	)
	t1 = time.time()
	for i in range(10):
		b = is_in_area(114.01, 33.32, grid_s.lons, grid_s.lats)
		print(b)
	print(time.time() - t1)
