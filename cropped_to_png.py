import cv2
import numpy as np
import os
import pydicom
import glob

root_path = 'CBIS-DDSM\\'
out_path = 'ROI_D\\'

if os.path.exists(root_path) is False:
	print('root_path does not exist')
	pass
	
for filename in glob.iglob(root_path + '**/*.dcm', recursive=True):
	ds = pydicom.read_file(filename)
	ori_img = ds.pixel_array
	height, width = ori_img.shape
	
	if width >= 1200:
		continue
		
	new_filename = os.path.basename(filename).replace(".dcm", ".png")
	new_path = os.path.dirname(filename).replace(root_path, out_path)
	if not os.path.exists(new_path):
		os.makedirs(new_path)
	out_file = new_path + "\\" + new_filename
	
	cv2.imwrite(out_file, ori_img)