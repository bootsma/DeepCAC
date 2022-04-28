import argparse
import csv
import shutil
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

import SimpleITK as sitk

def run_parser():
    parser = argparse.ArgumentParser(description="visualize_images.py\n Takes CAC scoring csv results output by "
                                                 "combine_results "
                                                 "and looks for the segmented CAC data and original volume to create "
                                                 "a visualization\n "
                                                 "of the results. The figures are output in 3rd step directory in"
                                                 "cropped_qc.")

    parser.add_argument('result_dir', type=str, help="Main output dir from DeepCAC")
    parser.add_argument('cac_file', type=str, help="CSV File from combine_results.py")
    return parser.parse_args()

def read_source_data(csv_filename):

    with open(csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        data = []
        for row in reader:
            data.append(row)

        return header, data

def plot_prediction(base_dir, id, img, cac_score=-1, deepcac_score=-1, slice_thickness = '?', show_fig = False):
    if id != '':
        base_filename = id + '.' + img
        file_pred = base_filename + '_pred.npy'
        file_img = base_filename + '_img.npy'
        file_img3071 = base_filename + '_img_3071.npy'
        file_orig_resampled = base_filename +'_img.nrrd'
    else:
        base_filename = img
        file_pred = base_filename + '_pred.npy'
        file_img = base_filename + '_img.npy'
        file_img3071 = base_filename + '_img_3071.npy'
        file_orig_resampled = base_filename +'_img.nrrd'

    resampled_dir = os.path.join(base_dir, 'step1_heartloc','resampled')

    model_dir = os.path.join(base_dir, 'step3_cacseg', 'model_output','npy')
    cropped_dir = os.path.join(base_dir, 'step3_cacseg', 'cropped')


    outdir = os.path.join(base_dir,'step4_cac_score', 'visuals')
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    try:

        filepath = os.path.join(model_dir, file_pred)
        prd = np.load(filepath)

        filepath = os.path.join(cropped_dir, file_img)
        img = np.load(filepath)

        filepath = os.path.join(cropped_dir, file_img3071)
        img3071 = np.load(filepath)

        filepath = os.path.join(resampled_dir, file_orig_resampled)
        nrrd_reader = sitk.ImageFileReader()
        nrrd_reader.SetFileName(filepath)
        img_resampled = nrrd_reader.Execute()
        img_resampled = sitk.GetArrayFromImage(img_resampled)
    except Exception as e:
        print('Could not load files, Exception: {}'.format(e))
        return outdir


    #print('p: ', prd.shape)
    #print('i: ', img.shape)
    #print('i3071: ', img3071.shape)

    mask_thresh = 0.1
    prd_mask = np.copy(prd)
    prd_mask[prd_mask < mask_thresh] = 0
    prd_mask[prd_mask > 0] = 1


    max_axis0 = np.sum(np.sum(prd_mask, axis=2), axis=1)
    index_axis0 = np.argmax(max_axis0)
    max_axis1 = np.sum(np.sum(prd_mask, axis=2), axis=0)
    index_axis1 = np.argmax(max_axis1)
    max_axis2 = np.sum(np.sum(prd_mask, axis=0), axis=0)
    index_axis2 = np.argmax(max_axis2)

    fig, ax = plt.subplots(3, 3, figsize=(32, 16))
    sz = img.shape

    ax[0, 0].imshow(img3071[index_axis0, :, :], cmap='gray')
    ax[0, 0].set_title('Slice index {}'.format(index_axis0))
    ax[0, 1].imshow(img3071[:, index_axis1, :], cmap='gray')
    ax[0, 1].set_title('Slice index {}'.format(index_axis1))
    ax[0, 2].imshow(img3071[:, :, index_axis2], cmap='gray')
    ax[0, 2].set_title('Slice index {}'.format(index_axis2))

    ax[1, 0].imshow(img3071[index_axis0, :, :], cmap='gray')
    ax[1, 1].imshow(img3071[:, index_axis1, :], cmap='gray')
    ax[1, 2].imshow(img3071[:, :, index_axis2], cmap='gray')
    ax[1, 0].imshow(prd_mask[index_axis0, :, :], cmap='jet', alpha=0.5)
    ax[1, 1].imshow(prd_mask[:, index_axis1, :], cmap='jet', alpha=0.5)
    ax[1, 2].imshow(prd_mask[:, :, index_axis2], cmap='jet', alpha=0.5)

    ax[2, 0].imshow(prd[index_axis0, :, :], cmap='gray')
    ax[2, 1].imshow(prd[:, index_axis1, :], cmap='gray')
    ax[2, 2].imshow(prd[:, :, index_axis2], cmap='gray')
    """
    ax[2, 0].imshow(prd[index_axis0, :, :], cmap='jet', alpha=0.5)
    ax[2, 1].imshow(prd[:, index_axis1, :], cmap='jet', alpha=0.5)
    ax[2, 2].imshow(prd[:, :, index_axis2], cmap='jet', alpha=0.5)
    """

    diff_score = float(deepcac_score) - float(cac_score)
    plt.suptitle('Slice Thickness: {}, CAC:{}, Deep-CAC:{}, Diff:{}'.format(slice_thickness,cac_score,deepcac_score, diff_score))
    fig.tight_layout()

    filename = os.path.join(outdir, base_filename)

    filename += '_step4_{}_pred.png'.format(abs(diff_score))

    plt.savefig(filename)
    if show_fig:
        plt.show()
    plt.close(fig)

    fig = plt.figure()


    plt.hist(img_resampled.flatten(), bins=range(-1024, 1024, 10), density = True)
    plt.title('Histogram {} - Slice Thickness {}'.format(base_filename, slice_thickness))
    filename = os.path.join(outdir, base_filename)
    filename += '_step1_hist_{}_pred.png'.format(abs(diff_score))
    plt.savefig(filename)
    if show_fig:
        plt.show()

    plt.close(fig)

    fig = plt.figure()
    plt.hist(img_resampled[img_resampled!=0].flatten(), bins=range(-1024, 1024, 16), density = True)
    plt.title('Histogram {} - Slice Thickness {}'.format(base_filename, slice_thickness))
    filename = os.path.join(outdir, base_filename)
    filename += '_step1_hist_ignore_0_{}_pred.png'.format(abs(diff_score))
    plt.savefig(filename)
    if show_fig:
        plt.show()

    plt.close(fig)



    model_dir_s1 = os.path.join(base_dir, 'step1_heartloc', 'model_output', 'png')
    model_dir_s2 = os.path.join(base_dir, 'step2_heartseg', 'model_output', 'png')
    model_dir_s3 =  os.path.join(base_dir, 'step3_cacseg', 'cropped_qc')
    file_img = base_filename + '_.png'
    try:
        file_cpy = base_filename + '_step1_loc.png'
        shutil.copyfile(os.path.join(model_dir_s1,file_img), os.path.join(outdir, file_cpy))
    except Exception as e:
        print('No image file for step1: {}'.format(e))

    try:
        file_cpy = base_filename + '_step2_seg.png'
        shutil.copyfile(os.path.join(model_dir_s2,file_img), os.path.join(outdir, file_cpy))
    except Exception as e:
        print('No image file for step2: {}'.format(e))

    try:
        file_img = base_filename + '.png'
        file_cpy = base_filename + '_step3_cacseg.png'
        shutil.copyfile(os.path.join(model_dir_s3,file_img), os.path.join(outdir, file_cpy))
    except Exception as e:
        print('No image file for step1: {}'.format(e))

    base_filename + '_.png'

    return outdir


if __name__ == "__main__":
    args = run_parser()
    header, data = read_source_data(args.cac_file)

    base_dir = args.result_dir


    cropped_qc_dir = os.path.join(base_dir, 'step3_cacseg', 'cropped_qc')

    print('Looking for data in: {}'.format(base_dir))

    # read data1
    index_id = header.index('RESEARCH_ID')

    #todo There can be more than one ImageId for a patient
    index_img = header.index('ImageId')
    index_cac_score = header.index('Cardiact CT CAC score')
    index_deepcac_score = header.index('DeepCAC CAC_pred')

    index_slice_thickness = header.index('SliceThickness')
    N= len(data)

    for i,row in enumerate(data):
        id = row[index_id] #'AB24600UN.R'
        img = row[index_img] #'CT_426cd8da-11237ca4-b7d2e943-4d51b36b-f1a352b5'
        cac_score =row[index_cac_score]
        deepcac_score= row[index_deepcac_score]
        slice_thickness = row[index_slice_thickness]
        outdir=plot_prediction(base_dir, id, img, cac_score, deepcac_score, slice_thickness)

        sys.stdout.write("\r<-- %d%% - Complete -->" % int(100*(i+1)/N))
        sys.stdout.flush()


    print('\nOutput data in: {}'.format(outdir))