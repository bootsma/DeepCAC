import argparse
import numpy as np
import h5py
import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_parser():
    parser = argparse.ArgumentParser(description="check_z_dist.py\n Finds all H5 data and calculates z-distribution. ")

    parser.add_argument('image_dir', type=str, help="Data containing images.")
    parser.add_argument('output_csv', type=str, help="Results csv.")

    return parser.parse_args()

if __name__ == "__main__":
    arg = run_parser()

    im_data={}

    header  = ['DicomFileName', 'Volume X', 'Volume Y', 'Volume Z', 'Spacing X', 'Spacing Y', 'Spacing Z', 'Z Length' ]
    dist =[]
    rows = []
    for file in os.listdir(arg.image_dir):
        if os.path.splitext(file)[1] == '.h5':

            file_path = os.path.join(arg.image_dir, file)
            h5py_data = h5py.File(file_path,'r',swmr=True)
            img_h5 = h5py_data['img'][0]
            print('shape o: {}'.format(img_h5.shape))
            h5_voxel_spacing = h5py_data['voxelSpacing']
            #img_sit = sitk.GetImageFromArray(img)
            height = h5_voxel_spacing[2]*img_h5.shape[2]
            rows.append( [os.path.splitext(file)[0], img_h5.shape[0], img_h5.shape[1], img_h5.shape[2],
                          h5_voxel_spacing[0],h5_voxel_spacing[1], h5_voxel_spacing[2],height])
            dist.append(height)

    with open(os.path.join(arg.image_dir, arg.output_csv),'wb') as csv_file:
        writer =  csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        writer.writerows(rows)

    fig = plt.figure()
    plt.hist(dist, 100)

    plt.title('Z Length Histogram, Mean={}, StDev={}, Median={}, Min={}, Max={}'.format(np.mean(dist),
                                                                                        np.std(dist), np.median(dist),
                                                                                        np.min(dist), np.max(dist)))
    plt.xlabel('Z Length')
    plt.ylabel('Image Count')
    plt.savefig(os.path.join(arg.image_dir, os.path.splitext(arg.output_csv)[0]+'.png'))
    print('Z Length Histogram, Mean={}, StDev={}, Median={}, Min={}, Max={}'.format(np.mean(dist),
                                                                                        np.std(dist), np.median(dist),
                                                                                        np.min(dist), np.max(dist)))