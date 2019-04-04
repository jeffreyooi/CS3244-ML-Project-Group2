import csv
import glob
import os

from shutil import copyfile

target_file = 'mass_case_description_train_set.csv'
output_file = 'mass_train_set.csv'

root_path = 'Training_D\\'
roi_path = 'ROI_D\\'

if not os.path.exists(root_path):
	print('root_path not found')
	pass

copyfile(target_file, output_file)

folders = {}
rois = {}
for folder in glob.iglob(root_path + '**/*.png', recursive=True):
	f = folder.replace(root_path, '')
	splited = f.split('\\')
	key = splited[0]
	folders[key] = f

for folder in glob.iglob(roi_path + '**/*.png', recursive=True):
	f = folder.replace(roi_path, '')
	splited = f.split('\\')
	key = splited[0] + splited[len(splited) - 1]
	rois[key] = f
	
csv_reader = csv.reader(open(target_file), delimiter=',')
lines = list(csv_reader)
l = 0
for row in lines:
	if l is 0:
		l += 1
		continue
	r = row[11]
	splited = r.split('/')
	k = splited[0]
	row[11] = folders[k]
	
	r = row[12]
	splited = r.split('/')
	k = splited[0] + splited[len(splited) - 1]
	row[12] = rois[k]

csv_writer = csv.writer(open(output_file, 'w', newline=''))
csv_writer.writerows(lines)