import os
import glob

ROOT_PATH = 'CBIS-DDSM-Calc-Test'

ROI_NAME = '000001'
CROP_NAME = '000000'

if not os.path.exists(ROOT_PATH):
    print('Path does not exist')

l = []
last_root = ''

for filename in glob.iglob(ROOT_PATH + '\\' + '**/*.dcm', recursive=True):
    if 'full' in filename:
        continue
    if last_root == '':
        last_root = os.path.dirname(filename)
        l.append(filename)
        continue
    if os.path.dirname(filename) not in last_root:
        #print(l)
        if len(l) == 2:
            first = os.stat(l[0])
            second = os.stat(l[1])
            if first.st_size < second.st_size:
                f = last_root + '\\' + 'temp.dcm'
                s = last_root + '\\' + 'temp2.dcm'
                
                os.rename(l[0], f)
                os.rename(l[1], s)
                
                roi = last_root + '\\' + ROI_NAME + '.dcm'
                crop = last_root + '\\' + CROP_NAME + '.dcm'

                os.rename(f, crop)
                os.rename(s, roi)
            else:
                f = last_root + '\\' + 'temp.dcm'
                s = last_root + '\\' + 'temp2.dcm'
                
                os.rename(l[0], f)
                os.rename(l[1], s)
                
                roi = last_root + '\\' + ROI_NAME + '.dcm'
                crop = last_root + '\\' + CROP_NAME + '.dcm'
                
                os.rename(s, crop)
                os.rename(f, roi)
            
        last_root = os.path.dirname(filename)
        l.clear()
        l.append(filename)
        continue
    
    l.append(filename)
