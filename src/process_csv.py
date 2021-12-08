import csv
import sys
from math import ceil



def read_and_filter_patients( csv_filename):
    with open(csv_filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        prev_row= None
        dicom_filename_index = header.index('DicomFileName')
        slice_thickness_index = header.index('SliceThickness')
        recon_diameter_index = header.index('ReconstructionDiameter')
        unique_patients = []
        for row in reader:
            new_patient = prev_row==None

            if prev_row is not None:
                new_patient = not prev_row[dicom_filename_index] == row[dicom_filename_index]



            if new_patient:
                print('New: {}'.format(row[dicom_filename_index]))
                unique_patients.append(row)
            else:
                slice_consistent = (prev_row[slice_thickness_index] == row[slice_thickness_index] and
                                    prev_row[recon_diameter_index] == row[recon_diameter_index])

                if not slice_consistent:
                    print('Patient Image: {} not consistent in Image: {}'.format(row[dicom_filename_index], row[0]))
                    unique_patients.pop()
                    print('Patient {} image set REMOVED'.format(row[1]))
            prev_row = row
        return header, unique_patients

def write_patient_csv( csv_filename, patient_data, header):
    with open(csv_filename, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        for patient in patient_data:
            writer.writerow(patient)



if __name__ == '__main__':
    args = sys.argv
    if len(sys.argv)==2:
        input_filename = sys.argv[1]
        header,unique_p = read_and_filter_patients(input_filename)
        output_filename = input_filename[:input_filename.rfind('.')]+'_h5.csv'
        write_patient_csv(output_filename, unique_p, header)
    elif len(sys.argv)==3:
        input_filename = sys.argv[1]
        header, unique_p = read_and_filter_patients(input_filename)
        output_filename = input_filename[:input_filename.rfind('.')]
        N = int(sys.argv[2])
        Ngroups = int(ceil(float(len(unique_p))/N))

        for i in range(Ngroups):
            curr_file = output_filename + "_{}_n{}_{}".format(i, N, '_h5.csv')
            if i == Ngroups-1:
                write_patient_csv(curr_file, unique_p[i*N:], header)
            else:

                write_patient_csv(curr_file, unique_p[i*N:(i+1)*N], header)


    else:
        print("\nUsage: process_csv patient_images.csv"
              "\n\tThis will read the csv file and create a new file called patient_iamges_h5.csv containing a line for each volume file."
              "\nUsage: process_csv patient_images.csv N"
              "\n\tThis will read the csv file and create multiple new csv files with N unique patient volumes in each csv file.")



