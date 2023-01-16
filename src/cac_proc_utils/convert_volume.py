
import argparse

import os
import h5py
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
def run_parser():
    parser = argparse.ArgumentParser(description="convert_image.py\n Takes a volume file loads it and converts to another type (based on file extension)")
    parser.add_argument('input_volume', type=str, help="input volume name")
    parser.add_argument('output_volume', type=str, help="output volume name)")
    parser.add_argument('-d', '--display', type=int, help="0- no display, 1-Show sag, axial, coronal, 2-Show sag")
    return parser.parse_args()

def convert_volumes(file_a, file_b, show_vol = int):
    #special case of h5 data
    input_img_sitk = None
    print('Reading {}'.format(file_a))
    if os.path.splitext(file_a)[1]=='.h5':
        h5py_data = h5py.File(file_a, 'r', swmr=True)
        input_img_sitk = sitk.GetImageFromArray(np.flip(np.transpose(h5py_data['img'][0], (2, 0, 1)), axis=0))
        input_img_sitk.SetSpacing(np.array(h5py_data['voxelSpacing']))
    else:
        img_sitk = sitk.ReadImage(file_a)

    if input_img_sitk is None:
        raise Exception('Image {} could not be loaded'.format(file_a))

    if show_vol == 1:
        img_cube = sitk.GetArrayFromImage(input_img_sitk)
        spacing = input_img_sitk.GetSpacing()
        print('Spacing: {}\t Size: {}'.format(spacing, input_img_sitk.GetSize()))
        fig, ax = plt.subplots(1, 3, figsize=(24, 8))
        ax[0].imshow(img_cube[int(img_cube.shape[0] / 2), :, :], cmap='gray')
        ax[0].set_aspect(spacing[2]/spacing[1])
        ax[1].imshow(img_cube[:, int(img_cube.shape[1] / 2), :], cmap='gray')
        ax[1].set_aspect(spacing[2] / spacing[0])
        ax[2].imshow(img_cube[:, :, int(img_cube.shape[2] / 2)], cmap='gray')
        ax[1].set_aspect(spacing[2] / spacing[1])

    if show_vol==2:
        img_cube = sitk.GetArrayFromImage(input_img_sitk)
        spacing = input_img_sitk.GetSpacing()
        print('Spacing: {}\t Size: {}'.format(spacing, input_img_sitk.GetSize()))
        fig, ax = plt.subplots(1, figsize=(16, 16))

        ax.imshow(img_cube[:, :, int(img_cube.shape[2] / 2)], cmap='gray')
        ax.invert_yaxis()
        ax.set_aspect(spacing[2] / spacing[1])


    if show_vol > 0:
        plt.title((os.path.split(file_a)[-1]))
        plt.savefig(os.path.splitext(file_b)[0]+'.png', bbox_inches='tight')
        plt.show()
        plt.close(fig)


    sitk.WriteImage( input_img_sitk, file_b)


if __name__ == '__main__':
    args = run_parser()
    convert_volumes(args.input_volume, args.output_volume, args.display)