import cv2
import numpy as np
import os
import pydicom
import glob

W = 400.

for filename in glob.iglob('**/*.dcm', recursive=True):
	ds = pydicom.read_file(filename)
	ori_img = ds.pixel_array
	height, width = ori_img.shape
	imgScale = W/width
	newX, newY = ori_img.shape[1] * imgScale, ori_img.shape[0] * imgScale
	newImg = cv2.resize(ori_img, (int(newX), int(newY)))
	newImg = newImg[200:600, 0:400]
	cv2.imwrite(filename.replace(".dcm", ".png"), newImg)
