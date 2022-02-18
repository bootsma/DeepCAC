import argparse
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from combine_results import read_deep_cac, read_source_data

def run_parser():
    parser = argparse.ArgumentParser(description="filter_results.py\n Removes rows from data with matching PatientID "
                                                 "Take input (input_cac_csv) and removes data listed in (remove_cac)")
    parser.add_argument('input_cac_csv', type=str, help="csv filename output from DeepCAC")
    parser.add_argument('remove_cac_csv', type=str, help="csv filename of data to remove")
    parser.add_argument('-f','--filter_key', nargs='?', const='PatientID',defualt = 'PatientID', type=str, help="header key to filter on, default: PatientID")
    return parser.parse_args()


"MS14735WT.R.CT_6e400182-ffb3f844-e29f9224-2d7ed0fb-864802bf"
"MS14735WT.R.CT_6e400182-ffb3f844-e29f9224-2d7ed0fb-864802bf"


if __name__ == "__main__":
    args = run_parser()

    source_header, source_data = read_source_data(args.input_cac_csv)
    remove_header, remove_data = read_source_data(args.remove_cac_csv)
    id_string = args.filter_key

    try:
        print("Looking for key: {}".format(id_string))

        source_id_index = source_header.index(id_string)
        remove_id_index = remove_header.index(id_string)
    except Exception as e:
        print("Couldn't find header key {} in both files.".format(id_string))
        print("Exception: {}".format(e))
        sys.exit()
    filter_list = [f[remove_id_index] for f in remove_data]

    fix_list = True
    if fix_list:
        filter_list = [f[:f.find('_')] + f[f.find('_'):f.rfind('_')] for f in filter_list]
#        print(filter_list)

    #print(filter_list[0] in filter_list)
    new_source_data =[ data for data in source_data if data[source_id_index] not in filter_list]




    out_filename = args.input_cac_csv[:args.input_cac_csv.rfind('.')] + '_filtered.csv'
    with open(out_filename,'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(source_header)
        writer.writerows(new_source_data)
        csv_file.close()


    original = len(new_source_data)

    ids = [ f[source_id_index] for f in new_source_data]
    patient_id = [ f[:f.rfind('.')] for f in ids]

    without_duplicates = len(set(patient_id))
    max_images=0


    print('Total Images after filtering: {}, total patients: {}'.format(original, without_duplicates))




