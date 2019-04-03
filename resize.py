import cv2
import numpy as np
import os
import pydicom

W = 400.

filename = '000000.dcm'
ds = pydicom.read_file(filename)
ori_img = ds.pixel_array
height, width = ori_img.shape
imgScale = W/width
newX, newY = ori_img.shape[1] * imgScale, ori_img.shape[0] * imgScale
newImg = cv2.resize(ori_img, (int(newX), int(newY)))
newImg = newImg[200:600, 0:400]
cv2.imwrite("000000.png", newImg)
