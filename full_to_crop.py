import cv2
import numpy as np
import os
import pydicom
import glob
import csv

target_width = 400.
root_path = 'CBIS-DDSM\\'
out_path = 'ROI_D\\'

process_full = False
process_roi = True

if os.path.exists(root_path) is False:
    print('root_path does not exist')
    pass

with open('crop_roi_new.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	for row in csv_reader:
		if len(row) == 0:
			continue
		if row[0] == '':
			continue
		
		file_name = row[0]
		rect_min_x = int(row[1])
		rect_min_y = int(row[2])
		rect_max_x = int(row[3])
		rect_max_y = int(row[4])
		print(file_name)
		new_filename = os.path.basename(file_name).replace(".dcm", ".png")
		new_path = os.path.dirname(file_name).replace(root_path, out_path)
		if not os.path.exists(new_path):
			os.makedirs(new_path)
		out_file = new_path + "\\" + new_filename
		
		ds = pydicom.read_file(file_name)
		ori_img = ds.pixel_array
		height, width = ori_img.shape
		
		if width < 1200:
			continue
		# Compute target scale
		img_scale = target_width / width
		new_x, new_y = int(ori_img.shape[1] * img_scale), int(ori_img.shape[0] * img_scale)

		new_img = cv2.resize(ori_img, (int(new_x), int(new_y)))
		# y then x
		#new_img = new_img[200:600, 0:400]
		
		x_width = rect_max_x - rect_min_x
		y_width = rect_max_y - rect_min_y
		center_x = int(rect_min_x + (x_width / 2))
		center_y = int(rect_min_y + (y_width / 2))
		
		half = target_width / 2
		
		remain_left 		= int(0 if (center_x - half) > 0 else (center_x - half))
		remain_right 		= int(0 if (center_x + half) < new_x else (center_x + half) - new_x)
		remain_top 			= int(0 if (center_y - half) > 0 else (center_y - half))
		remain_bottom 		= int(0 if (center_y + half) < new_y else (center_y + half) - new_y)
		
		top = center_y - half - + remain_top - remain_bottom
		bottom = center_y + half - + remain_bottom - remain_top
		
		new_img = new_img[int(top):int(bottom), 0:int(target_width)]
		cv2.imwrite(out_file, new_img)