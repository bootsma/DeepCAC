import argparse
import csv
import os
import sys
from math import ceil



def read_and_filter_patients( csv_filename, debug = False):
    with open(csv_filename, 'r') as csv_file:
        print( 'Reading ' , csv_filename)
        reader = csv.reader(csv_file)
        header = next(reader)
        prev_row= None
        dicom_filename_index = header.index('DicomFileName')
        slice_thickness_index = header.index('SliceThickness')
        recon_diameter_index = header.index('ReconstructionDiameter')
        unique_patients = []
        skipped_patients = []
        patient_popped = False
        total_skipped = 0
        row_count = 0
        for row in reader:
            new_patient = prev_row==None
            row_count+=1

            if prev_row is not None:
                new_patient = not prev_row[dicom_filename_index] == row[dicom_filename_index]



            if new_patient:
                if debug:
                    print('New: {}, Row: {}'.format(row[dicom_filename_index], row_count))
                unique_patients.append(row)
                patient_popped = False
            else:
                slice_consistent = (prev_row[slice_thickness_index] == row[slice_thickness_index] and
                                    prev_row[recon_diameter_index] == row[recon_diameter_index])

                if not slice_consistent:
                    if debug:
                        print('Patient Image: {} not consistent in Image Slice: {}'.format(row[dicom_filename_index], row[0]))
                    if not patient_popped:
                        skipped_patients.append( unique_patients.pop())
                        print('Patient {} image set REMOVED do inconsistencies'.format(row[1]))
                        patient_popped = True
                        total_skipped += 1
            prev_row = row
        print( 'Total Unique Patients Found: {}, Skipped: {}'.format(total_skipped+len(unique_patients), total_skipped))
        return header, unique_patients,skipped_patients

def write_patient_csv( csv_filename, patient_data, header):
    print('Writing data to file: {}'.format(csv_filename))
    with open(csv_filename, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        for patient in patient_data:
            writer.writerow(patient)

def run_parser():
    parser = argparse.ArgumentParser(description="process_csv.py\n Takes the dicom header csv and finds the unique images"
                                                 "and writes out a new csv file with just the unique image data.")
    parser.add_argument('input_csv', type=str, help="csv filename with the dicom header info")
    parser.add_argument('-s','--split', type=int, help="number to put into each output csv file, splits data up into separate files")
    parser.add_argument('-t', '--type_split', action='store_true', help="Splits the data into cardiac and ct data")
    return parser.parse_args()


if __name__ == '__main__':

    args = run_parser()

    if args.type_split and args.split:
        raise Exception("Only one type of data splitting currently supported")
    print('... ', os.getcwd())
    input_filename = args.input_csv
    try:
        header,unique_p,skipped_patients = read_and_filter_patients(input_filename)
    except Exception as e:
        print('File open error: {}, Exception: {}'.format(input_filename, e))
        raise e


    #if len(sys.argv) == 2:
    output_filename = input_filename[:input_filename.rfind('.')] + '_h5.csv'
    write_patient_csv(output_filename, unique_p, header)

    skipped_filename = input_filename[:input_filename.rfind('.')] + '_skipped_h5.csv'
    write_patient_csv(skipped_filename, skipped_patients, header)

    if args.type_split:
        print("Splitting between Cardiac and CT")
        dicom_filename_index = header.index('DicomFileName')
        ct_p = []
        cardiac_p = []
        unknown_p = []
        for p in unique_p:
            if p[dicom_filename_index][0:2]=="CT":
                ct_p.append(p)
            elif p[dicom_filename_index][0:7]=="CARDIAC":
                cardiac_p.append(p)
            else:
                unknown_p.append(p)
        print("\t[CARDIAC, CT, UNKNOWN]:[{},{},{}]".format(len(cardiac_p),len(ct_p),len(unknown_p)))

        if len(ct_p)>0:
            output_filename = input_filename[:input_filename.rfind('.')] + '_CT_h5.csv'
            write_patient_csv(output_filename, ct_p, header)
        if len(cardiac_p)>0:
            output_filename = input_filename[:input_filename.rfind('.')] + '_CARDIAC_CT_h5.csv'
            write_patient_csv(output_filename, cardiac_p, header)
        if len(unknown_p) >0:
            output_filename = input_filename[:input_filename.rfind('.')] + '_UNKNOWN_h5.csv'
            write_patient_csv(output_filename, unknown_p, header)



    elif args.split:
        output_filename = input_filename[:input_filename.rfind('.')]
        N = int(sys.argv[2])
        Ngroups = int(ceil(float(len(unique_p))/N))

        for i in range(Ngroups):
            curr_file = output_filename + "_{}_n{}_{}".format(i, N, '_h5.csv')
            if i == Ngroups-1:
                write_patient_csv(curr_file, unique_p[i*N:], header)
            else:

                write_patient_csv(curr_file, unique_p[i*N:(i+1)*N], header)




