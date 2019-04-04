import cv2
import numpy as np
import os
import pydicom
import glob
import csv

# The root path of the images from CBIS-DDSM
root_path = 'CBIS-DDSM\\'

# Threshold for extracting outline of ROI
threshold = 100

if not os.path.exists(root_path):
	print('root_path does not exist')
	pass

targetWidth = 400

# 0 for writing for full, 1 for writing for ROI
mode = 1

with open('crop_roi_new.csv', mode='w') as csv_file:
	last_id = ''
	list_id = []
	crop_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	x = 10000
	y = 10000
	newWidth = 0
	newHeight = 0
	for filename in glob.iglob(root_path + '**/*.dcm', recursive=True):
		if "full" in filename:
			if mode is 1:
				for id in list_id:
					list_to_write = [id, x, y, newWidth, newHeight]
					crop_writer.writerow(list_to_write)
				list_id = []
			elif mode is 0:
				list_to_write = [last_id, x, y, newWidth, newHeight]
				crop_writer.writerow(list_to_write)
				last_id = filename
			x = 10000
			y = 10000
			newWidth = 0
			newHeight = 0
			continue
		print(filename)
		try:
			ds = pydicom.read_file(filename)
			ori_img = ds.pixel_array
			height, width = ori_img.shape
			
			# Assuming cropped dcm images are of width lesser than 1200, we skip
			if width < 1200:
				continue
				
			# Edge detection
			imgScale = targetWidth / width
			newX, newY = ori_img.shape[1] * imgScale, ori_img.shape[0] * imgScale
			ori_img = cv2.resize(ori_img, (int(newX), int(newY)))
			ori_img = cv2.blur(ori_img, (3, 3))
			ori_img = np.uint8(ori_img)
			canny_output = cv2.Canny(ori_img, threshold, threshold * 2)
			
			# Contour extraction
			contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			contours_poly = [None] * len(contours)
			boundRect = [None] * len(contours)
			for i, c in enumerate(contours):
				contours_poly[i] = cv2.approxPolyDP(c, 3, True)
				boundRect[i] = cv2.boundingRect(contours_poly[i])
				
			#drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype = np.uint8)
			
			rect_min_x = 10000
			rect_max_x = 0
			rect_min_y = 10000
			rect_max_y = 0
			
			for i in range(len(contours)):
				#color = (255, 0, 0)
				#cv2.drawContours(drawing, contours_poly, i, color)
				#cv2.rectangle(drawing, (int(boundRect[i][0]), int(boundRect[i][1])), (int(boundRect[i][0] + boundRect[i][2]), int(boundRect[i][1] + boundRect[i][3])), color, 2)
				rect_min_x = min(rect_min_x, int(boundRect[i][0]))
				rect_max_x = max(rect_max_x, int(boundRect[i][0] + boundRect[i][2]))
				rect_min_y = min(rect_min_y, int(boundRect[i][1]))
				rect_max_y = max(rect_max_y, int(boundRect[i][1] + boundRect[i][3]))
			
			#color = (0, 0, 255)
			#cv2.rectangle(drawing, (rect_min_x, rect_min_y), (rect_max_x, rect_max_y), color, 2)
		
			x = min(rect_min_x, x)
			y = min(rect_min_y, y)
			newWidth = max(rect_max_x, newWidth)
			newHeight = max(rect_max_y, newHeight)

			if mode is 1:
				list_id.append(filename)
			#list_to_write = [last_id, x, y, newWidth, newHeight]
			#crop_writer.writerow(list_to_write)
		except Exception as e:
			list_to_write = [last_id, x, y, newWidth, newHeight]
			print(e)
	
	if mode is 1:
		for id in list_id:
			list_to_write = [id, x, y, newWidth, newHeight]
			crop_writer.writerow(list_to_write)
	elif mode is 0:
		list_to_write = [last_id, x, y, newWidth, newHeight]
		crop_writer.writerow(list_to_write)