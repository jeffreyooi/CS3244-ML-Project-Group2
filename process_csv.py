import csv
import glob
import os
from shutil import copyfile
import sys

class CSVProcessor:
    def __init__(self, in_file, out_file, root_dir):
        self.in_file = in_file
        self.out_file = out_file
        self.root_dir = root_dir

    # Validate processed files to ensure that no data is missing
    def validate(self):
        csv_reader = csv.reader(open(self.in_file), delimiter=',')
        rows = list(csv_reader)
        l = []
        for row in rows:
            if row[0] == 'patient_id':
                continue
            path_to_open = row[0] + '\\' + row[2] + '_' + row[3] + '_' + row[4]
            validate_path = self.root_dir + '\\' + path_to_open
            
            if not os.path.exists(validate_path):
                l.append(validate_path)

        return l

    def process(self):
        copyfile(self.in_file, self.out_file)

        csv_reader = csv.reader(open(self.out_file), delimiter=',')
        rows = list(csv_reader)

        for row in rows:
            if row[0] == 'patient_id':
                del row[12]
                continue
            path_to_open = row[0] + '\\' + row[2] + '_' + row[3] + '_' + row[4]
            validate_path = self.root_dir + '\\' + path_to_open
            
            if not os.path.exists(validate_path):
                print(validate_path)
                continue
            
            row[11] = path_to_open + '\\' + 'full.png'
            row[13] = path_to_open + '\\' + 'roi.png'
            
            del row[12]
        
        csv_writer = csv.writer(open(self.out_file, 'w', newline=''))
        csv_writer.writerows(rows)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: <in_file> <out_file> <root_dir>')
        print('in_file:\tThe csv to modify')
        print('out_file:\tThe csv file name to output')
        print('root_dir:\tThe root directory of processed files')
    else:
        p = CSVProcessor(sys.argv[1], sys.argv[2], sys.argv[3])
        l = p.validate()
        if len(l) > 0:
            print('There are missing files!')
            for f in l:
                print(f)
        else:
            p.process()