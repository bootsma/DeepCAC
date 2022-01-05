import argparse
import csv


def run_parser():
    parser = argparse.ArgumentParser(description="combine_results.py\n Takes CAC scoring csv results output by DeepCAC "
                                                 "(deep_cac_csv) and combines them with CAC scores from another source (source_cac)")
    parser.add_argument('deep_cac_csv', type=str, help="csv filename output from DeepCAC")
    parser.add_argument('source_cac_csv', type=str, help="csv filename of additional CAC scores")
    return parser.parse_args()

def read_source_data(csv_filename):

    with open(csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        data = []
        for row in reader:
            data.append(row)

        return header, data



def read_deep_cac(csv_filename):
    """

    Args:
        csv_filename ():

    Returns:
        Dictionary with PatientID as key and element a tuple of (CAC Score, CAC class)
    """

    cac_string = 'CAC_pred'
    cac_class_string = 'Class_pred'
    id_string = 'PatientID'
    data = {} #dictionary with id as index then tuple of cac and class
    with open(csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        id_index = header.index(id_string)
        cac_index = header.index(cac_string)
        class_index = header.index(cac_class_string)
        for row in reader:
            if data.get(row[id_index]) is None:
                data[row[id_index]] = (row[cac_index], row[class_index])
            else:
                raise Exception('Duplicates of ID {} exist in csv {}.'.format(row[id_index], csv_filename))

    return data


def combine_csv_data(output_filename, deepcac_data, source_header, source_data, source_add=true):
    with open(output_filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        new_header = source_header
        new_header.append('DeepCAC CAC_pred')
        new_header.append('DeepCAC Class_pred')
        writer.writerow(new_header)
        source_id_index = new_header.index('RESEARCH_ID')
        if source_add:
            for data in source_data:

                id = data[source_id_index]
                pred_vals = deepcac_data.get(id)
                if pred_vals is None:
                    print('No DeepCAC predictions for ID:{}'.format(id))
                    data.append('')
                    data.append('')
                else:
                    data.append(pred_vals[0])
                    data.append(pred_vals[1])

                writer.writerow(data)
            else:
                source_ids = [ row[source_id_index] for row in source_data]
                for key, item in deepcac_data.items():
                    curr_index = source_ids.index(key)






if __name__ == "__main__":

    args = run_parser()
    data = read_deep_cac(args.deep_cac_csv)
    source_header, source_data = read_source_data(args.source_cac_csv)

    output_filename = args.source_cac_csv[:args.source_cac_csv.rfind('.')] + '_deepcac.csv'
    combine_csv_data(output_filename, data, source_header, source_data)




