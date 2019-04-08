# For computing bounding box of ROIs
import cv2
# For traversing folders
import glob
# For matrices
import numpy as np
# For checking if path exists
import os
# For opening DICOM files
import pydicom
# Regular expression
import re
# For retrieving arguments from console
import sys

# CV Canny properties
THRESHOLD = 100

class Processor:
    def __init__(self, root_path, out_path_full, out_path_roi, roi_name, target_width, crop_width):
        self.root_path = root_path
        self.out_path_full = out_path_full
        self.out_path_roi = out_path_roi
        self.roi_name = roi_name
        self.target_width = int(target_width)
        self.crop_width = int(crop_width)

        self.resize = cv2.resize

    def retrieve_rect_coords(self, pixel_arr):
        ori_img = pixel_arr
        ori_img = cv2.blur(ori_img, (3, 3))
        ori_img = np.uint8(ori_img)
        canny = cv2.Canny(ori_img, THRESHOLD, THRESHOLD * 2)

        contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_poly, bound_rect = [None] * len(contours), [None] * len(contours)

        for i, c in enumerate(contours):
            contours_poly[i] = cv2.approxPolyDP(c, 3, True)
            bound_rect[i] = cv2.boundingRect(contours_poly[i])

        rect_min_x = 10000
        rect_max_x = 0
        rect_min_y = 10000
        rect_max_y = 0

        for i in range(len(contours)):
            rect_min_x = min(rect_min_x, int(bound_rect[i][0]))
            rect_max_x = max(rect_max_x, int(bound_rect[i][0] + bound_rect[i][2]))
            rect_min_y = min(rect_min_y, int(bound_rect[i][1]))
            rect_max_y = max(rect_max_y, int(bound_rect[i][1] + bound_rect[i][3]))

        return rect_min_x, rect_max_x, rect_min_y, rect_max_y

    def convert_to_png(self, file_name, out_path, pixel_arr):
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        out_file = out_path + "\\" + file_name
        cv2.imwrite(out_file, pixel_arr)

    def write_img(self, file_name, out_path, pixel_arr, x, y, x_width, y_height):
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        out_file = out_path + file_name
        try:
            half = self.crop_width / 2
            center_x = x + ((x_width - x) / 2)
            center_y = y + ((y_height - y) / 2)

            height, width = pixel_arr.shape

            remain_left = 0 if (center_x - half) >= 0 else -(center_x - half)
            remain_right = 0 if (center_x + half) <= width else (center_x + half) - width

            remain_top = 0 if (center_y - half) >= 0 else -(center_y - half)
            remain_bottom = 0 if (center_y + half) <= height else (center_y + half) - height

            left = 0 if remain_left > 0 else center_x - half - remain_right
            right = width if remain_right > 0 else center_x + half + remain_left

            top = 0 if remain_top > 0 else center_y - half - remain_bottom
            bottom = height if remain_bottom > 0 else center_y + half + remain_top

            new_img = pixel_arr[int(top):int(bottom), int(left):int(right)]
            cv2.imwrite(out_file, new_img)
        except Exception as e:
            print(e)

    def rescale_img(self, pixel_arr):
        h, w = pixel_arr.shape
        img_scale = self.target_width / w
        new_x, new_y = pixel_arr.shape[1] * img_scale, pixel_arr.shape[0] * img_scale
        return self.resize(pixel_arr, (int(new_x), int(new_y)))

    def extract_patient_id(self, filepath):
        m = re.search('([P][_][0-9]+)', filepath)
        patient_id = ''
        if m:
            patient_id = m.group(1)
        return patient_id

    def format_output_path(self, filepath):
        new_file_path = ''
        
        patient_id = self.extract_patient_id(filepath)
        patient_id_idx = filepath.find(patient_id)

        start_idx = patient_id_idx + len(patient_id) + 1

        f = filepath[start_idx:]
        split = f.split('\\')
        
        new_file_path = patient_id + '\\' + split[0] + '\\'
        return new_file_path

    def process(self):
        print('Begin processing')
        file_filter = '**/*.dcm'
        full_to_process = ''
        rect_coords = self.retrieve_rect_coords
        dicom_reader = pydicom.read_file

        for filename in glob.iglob(self.root_path + '\\' + file_filter, recursive=True):
            if 'full' in filename:
                full_to_process = filename
                continue
            
            if self.roi_name not in filename:
                continue

            roi_ds = dicom_reader(filename)
            roi_arr = roi_ds.pixel_array
            scaled_roi_arr = self.rescale_img(roi_arr)
            temp_x, temp_x_width, temp_y, temp_y_height = rect_coords(scaled_roi_arr)
            
            new_file_path = self.format_output_path(filename)
            new_file_path = self.out_path_full + '\\' + new_file_path

            full_ds = dicom_reader(full_to_process)
            full_arr = full_ds.pixel_array
            scaled_full_arr = self.rescale_img(full_arr)

            self.write_img('full.png', new_file_path, scaled_full_arr, temp_x, temp_y, temp_x_width, temp_y_height)
            self.write_img('roi.png', new_file_path, scaled_roi_arr, temp_x, temp_y, temp_x_width, temp_y_height)


    def compute_bounding_box(self):
        full_id = ''
        roi_ids = []
        roi_arrs = []
        x = 10000
        y = 10000
        x_width = 0
        y_height = 0
        file_filter = '**/*.dcm'
        rect_coords = self.retrieve_rect_coords
        rid_append = roi_ids.append
        rarr_append = roi_arrs.append
        full_count = 0
        roi_count = 0
        cropped_count = 0
        for filename in glob.iglob(self.root_path + "\\" + file_filter, recursive=True):
            if 'full' in filename:
                if full_id is '':
                    full_id = filename
                    continue
                try:
                    new_filename = os.path.basename(full_id).replace(".dcm", ".png")
                    new_path = os.path.dirname(full_id).replace(self.root_path, self.out_path_full)
                    full_arr = self.dicom_reader(full_id)
                    pixel_arr = full_arr.pixel_array
                    scaled = self.rescale_img(pixel_arr)
                    self.write_img(new_filename, new_path, scaled, x, y, x_width, y_height)
                    full_count += 1
                    for i in range(len(roi_ids)):
                        new_filename = os.path.basename(roi_ids[i]).replace(".dcm", ".png")
                        new_path = os.path.dirname(roi_ids[i]).replace(self.root_path, self.out_path_roi)
                        self.write_img(new_filename, new_path, roi_arrs[i], x, y, x_width, y_height)
                        roi_count += 1

                    full_id = filename
                    roi_ids.clear()
                    roi_arrs.clear()
                    x = 10000
                    y = 10000
                    x_width = 0
                    y_height = 0
                except Exception as e:
                    print(e)
                continue
            if self.roi_name not in filename:
                new_filename = os.path.basename(filename).replace(".dcm", ".png")
                new_path = os.path.dirname(filename).replace(self.root_path, self.out_path_roi)
                ds = self.dicom_reader(filename)
                px = ds.pixel_array
                self.convert_to_png(new_filename, new_path, px)
                cropped_count += 1
                continue
            try:
                ds = self.dicom_reader(filename)
                pixel_arr = ds.pixel_array
                scaled_arr = self.rescale_img(pixel_arr)

                temp_x, temp_x_width, temp_y, temp_y_height = rect_coords(scaled_arr)
                x = min(x, temp_x)
                y = min(y, temp_y)
                x_width = max(x_width, temp_x_width)
                y_height = max(y_height, temp_y_height)
                rid_append(filename)
                rarr_append(scaled_arr)
            except Exception as e:
                pass
        # Writing for the last one
        new_filename = os.path.basename(full_id).replace(".dcm", ".png")
        new_path = os.path.dirname(full_id).replace(self.root_path, self.out_path_full)
        full_arr = self.dicom_reader(full_id)
        pixel_arr = full_arr.pixel_array
        scaled = self.rescale_img(pixel_arr)
        self.write_img(new_filename, new_path, scaled, x, y, x_width, y_height)
        full_count += 1
        for i in range(len(roi_ids)):
            new_filename = os.path.basename(roi_ids[i]).replace(".dcm", ".png")
            new_path = os.path.dirname(roi_ids[i]).replace(self.root_path, self.out_path_roi)
            self.write_img(new_filename, new_path, roi_arrs[i], x, y, x_width, y_height)
            roi_count += 1
        print("Processed full mammogram: " + str(full_count))
        print("Processed ROI: " + str(roi_count))
        print("Processed cropped: " + str(cropped_count))

# main method
if __name__ == '__main__':
    if len(sys.argv) != 7:
        print('Usage: <root_path> <output_path_full> <output_path_roi> <roi_label> <target_width>')
        print('root_path:\t\tThe root path that contains all full mammogram and ROI dicom images.')
        print('output_path_full:\tThe output path to write processed full mammogram files')
        print('output_path_roi:\tThe output path to write processed ROI and cropped images mammogram files')
        print('roi_label:\t\tThe ROI DICOM file name (check the description CSV)')
        print('target_width:\t\tThe target width of the processed files')
    else:
        p = Processor(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        #p.compute_bounding_box()
        #print(p.format_output_path('CBIS-DDSM-Mass-Train\\Mass-Training_P_00001_LEFT_CC\\07-20-2016-DDSM-74994\\1-full mammogram images-24515'))
        p.process()    