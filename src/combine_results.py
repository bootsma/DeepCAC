import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def run_parser():
    parser = argparse.ArgumentParser(description="combine_results.py\n Takes CAC scoring csv results output by DeepCAC "
                                                 "(deep_cac_csv) and combines them with CAC scores from another source (source_cac)")
    parser.add_argument('deep_cac_csv', type=str, help="csv filename output from DeepCAC")
    parser.add_argument('source_cac_csv', type=str, help="csv filename of additional CAC scores")
    parser.add_argument('-p','--plot',action='store_true')
    return parser.parse_args()

def read_source_data(csv_filename):

    with open(csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        data = []
        for row in reader:
            data.append(row)

        return header, data



def read_deep_cac(csv_filename ):
    """

    Args:
        csv_filename ():

    Returns:
        Dictionary with PatientID as key and element a tuple of (CAC Score, CAC class)
    """
    max_images_per_patient = 0
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

            id = row[id_index]
            last_dot = id.rfind('.')
            patient_id = id[:last_dot]
            image_id = id[last_dot + 1:]
            print('adding {}'.format(patient_id))
            element = data.get(patient_id)
            if element is None:
                data[patient_id] = [image_id, row[cac_index], row[class_index]]

                if max_images_per_patient == 0:
                    max_images_per_patient=1
            else:
                element.append(image_id)
                element.append(row[cac_index])
                element.append(row[class_index])
                nimages = int(len(element)/3)
                if nimages > max_images_per_patient:
                    max_images_per_patient = nimages
                #raise Exception('Duplicates of ID {} exist in csv {}.'.format(row[id_index], csv_filename))

    return data, max_images_per_patient


def combine_csv_data(output_filename, deepcac_data, source_header, source_data, max_images_per_patient, source_add=True):

    with open(output_filename, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        new_header = source_header
        for i in range(max_images_per_patient):
            new_header.append('ImageId')
            new_header.append('DeepCAC CAC_pred')
            new_header.append('DeepCAC Class_pred')
        writer.writerow(new_header)
        source_id_index = new_header.index('RESEARCH_ID')



        new_data =[]
        for data in source_data:
            id = data[source_id_index]
            pred_vals = deepcac_data.get(id)
            exist = False
            if pred_vals is None:
                print('No DeepCAC predictions for ID:{}'.format(id))

                data.append('')
                data.append('')
            else:
                exist = True
                for val in pred_vals:
                    data.append(val)

            if source_add:
                writer.writerow(data)
                new_data.append(data)
            elif not source_add and exist:
                writer.writerow(data)
                new_data.append(data)
        return new_data, new_header




if __name__ == "__main__":

    args = run_parser()
    data, max_images_per_patient = read_deep_cac(args.deep_cac_csv)
    print(data)
    print('MAX: {}'.format(max_images_per_patient))
    source_header, source_data = read_source_data(args.source_cac_csv)

    output_filename = args.source_cac_csv[:args.source_cac_csv.rfind('.')] + '_deepcac.csv'
    combined_data, combined_header = combine_csv_data(output_filename, data, source_header, source_data, max_images_per_patient,False)
    if args.plot:
        truth_cac_index = combined_header.index('Chest CT CAC Visual score (0 absent, 1 mild, 2 moderate, 3 severe)')
        deep_cac_index = combined_header.index('DeepCAC Class_pred')

        diff_cac =[float(x[deep_cac_index])- float(x[truth_cac_index]) for x in combined_data]
        bin_list = [-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5]
        plt.hist(diff_cac,bins = bin_list,density =True)

        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.ylabel('Percent of Patients (N Patients = {})'.format(len(combined_data)))
        plt.xlabel('[Chest CT CAC Visual Score] -[Deep CAC Class]')
        plt.title('CAC Class Error Distribution')
        plt.show()

        truth_cac_index = combined_header.index('Cardiact CT CAC score')
        deep_cac_index = combined_header.index('DeepCAC CAC_pred')
        truth_cac_score = [float(x[truth_cac_index]) for x in combined_data]
        pred_cac_score = [float(x[deep_cac_index]) for x in combined_data]

        plt.plot(truth_cac_score, pred_cac_score,'o')

        m,b=np.polyfit(truth_cac_score,pred_cac_score,1)
        plt.plot(truth_cac_score, m*np.array(truth_cac_score)+b)
        maxval = max([max(truth_cac_score ), max(pred_cac_score)])
        plt.xlim([0, maxval])
        plt.ylim([0, maxval])
        plt.xlabel('Cardiac CT CAC Score')
        plt.ylabel('DeepCAC Predicted CAC Score')
        corr = np.corrcoef(truth_cac_score, pred_cac_score)[0,1]
        plt.text(500,3000, 'Fit: y={:.2f}x+{:.2f}\nCorrelation(x,y)={:.2f}'.format(m,b,corr))
        plt.show()
        print('Correlation: {}'.format(corr))






