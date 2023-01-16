#Find data < than length
#Write simple list of this data
#Find mismatched voxel z

import argparse
import csv
import os
import sys
from math import ceil
def run_parser():
    parser = argparse.ArgumentParser(description="collate_image_csv_data.py\n Takes the dicom header csv "
                                                 "(output from process_csv) and height/volume info (output from check_z_dist)")
    parser.add_argument('input_csv_a', type=str, help="csv filename with the dicom header info")
    parser.add_argument('input_csv_b', type=str, help="csv filename with volume information from h5 data (output of check_z_dist)")
    parser.add_argument('output_csv', type=str, help="output csv base filename (no ext)")
    parser.add_argument('-c','--z_cutoff', type=int, help="number to put into ")

    return parser.parse_args()

def read_csv_data(csv_filename, header=[], data_dict=None):
    print(os.getcwd())
    with open(csv_filename, 'r') as csv_file:
        print( 'Reading ' , csv_filename)
        reader = csv.reader(csv_file)


        if data_dict is None:
            data_dict = {}
            new_data = True

        else:
            new_data = False

        header_new = next(reader)
        header+=header_new
        id_index = header_new.index('DicomFileName')

        for row in reader:
            id = os.path.splitext(row[id_index])[0]


            d = data_dict.get(id)
            if d is None and new_data is False:
                msg = 'Missing data for {} '.format(id)
                print(msg)
                raise Exception(msg)

            if d is not None and new_data:
                msg = 'Duplicate data for {} '.format(id)
                print(msg)
                raise Exception(msg)

            if d is None:
                data_dict[id] = row
            else:
                data_dict[id] +=row

    return header, data_dict



def write_csv_file(csv_filename, rows, header):
    print('Writing data to file: {}'.format(csv_filename))
    with open(csv_filename, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

def main():
    args = run_parser()
    header, data_dict = read_csv_data(args.input_csv_a)

    header, data_dict = read_csv_data(args.input_csv_b, header, data_dict)

    full_filename = args.output_csv + '_all.csv'
    write_csv_file(full_filename, data_dict.values(), header)

    pat_id = header.index('PatientID')
    dicom_id = header.index('DicomFileName')
    descrip_id = header.index('SeriesDescription')
    z_length = header.index('Z Length')
    z_vox = header.index('Volume Z')
    n_slices = header.index('Number of Slices')

    z_items = []
    slice_count_mismatch = []
    for key,item in data_dict.items():
        if float(item[z_length]) <= args.z_cutoff:
            z_items.append(item)

        if int(item[z_vox]) != int(item[n_slices]):
            slice_count_mismatch.append(item)

    write_csv_file(args.output_csv+'_shortz.csv', z_items, header)
    write_csv_file(args.output_csv+'_mismatchSliceCount.csv',slice_count_mismatch, header)
    





if __name__ == "__main__":
    main()