"""
Converts numpy data of CAC segmentation and segmented heart image to nifti data for visualization in itk-snap
"""
import argparse
import os
import SimpleITK as sitk
import numpy as np

out_vol_type='.nii.gz'

def run_parser():
    parser = argparse.ArgumentParser(description="Create readable volume data from step 3 of algorithm.")
    parser.add_argument('data_dir', type=str, help="Main output dir from DeepCAC")
    return parser.parse_args()

def convert(img_file, out_dir, is_mask=False):

    sitk_img = None

    if os.path.splitext(img_file)[-1] == '.npy':
        data = np.load(img_file)
        if is_mask:
            data[data<0.1]=0
            data[data>0]=1
            data = data.astype('int16')


        sitk_img = sitk.GetImageFromArray(data)

    else:
        sitk_img = sitk.ReadImage(img_file)

    new_filename = os.path.join(out_dir,
                                os.path.splitext(os.path.split(img_file)[-1])[0] + out_vol_type)

    print('Converting {} -> {} '.format(img_file, new_filename))

    sitk_img.SetSpacing([0.68,0.68,2.5])
    sitk.WriteImage(sitk_img, new_filename)

def add_spacing_all_vols( dir ):
    files = os.listdir(dir)
    files = [file for file in files if 'nii.gz' in file]
    for file in files:
        print(file)
        im = sitk.ReadImage(os.path.join(dir, file))
        im.SetSpacing([0.68, 0.68, 2.5])

        sitk.WriteImage(im, file)



def run_conversion(data_dir, step_dirs = ['step1_heartloc', 'step2_heartseg', 'step3_cacseg',  'step4_cac_score'],
                   output_dir = 'segmentations', out_vol_type = '.nii.gz'):

    step_paths = []
    for directory in step_dirs:
        path = os.path.join(data_dir, directory)
        if not os.path.isdir(path):
            raise IOError( 'Missing directory {}'.format(path))
        step_paths.append(path)

    mask_dir = os.path.join(step_paths[2],'model_output', 'npy')
    mask_files = os.listdir(mask_dir)
    mask_files = [file for file in mask_files if os.path.splitext(file)[-1] == '.npy']
    img_dir = os.path.join(step_paths[2],'cropped')
    img_files = os.listdir(img_dir)
    img_files = [file for file in img_files if '_img_3071.npy' in file]

    out_dir = os.path.join(data_dir,'step5_analysis',output_dir)
    if not os.path.isdir(out_dir):
        os.makedirs( out_dir)

    for img_file in img_files:
        convert(os.path.join(img_dir,img_file), out_dir)

    for img_file in mask_files:
        convert(os.path.join(mask_dir,img_file), out_dir, True)

if __name__ == '__main__':
    add_spacing_all_vols('C:\\Users\\Gregory\\OneDrive - UHN\\Projects\\JDMI-AI\\CAC-Scoring\\Kate_Segmentations\\segmentations')
#    args = run_parser()
#    run_conversion(args.data_dir)




















