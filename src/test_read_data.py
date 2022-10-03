
import os
import shutil

import numpy as np
import h5py
import csv
import SimpleITK as sitk
import matplotlib.pyplot as plt
def plot_im( img, msk_img, spacing, title, save_file=None):
    print('Image {}, Mask {}'.format(img.shape, msk_img.shape))

    num_slices=3
    fig, ax = plt.subplots(2, num_slices, figsize=(10,7))
    #fig.suptitle('{}, spacing {}, size {}'.format(title, [round(s,2) for s in spacing], msk_img.shape))
    fig.suptitle(title,fontsize=16)

    blank = np.ones(img[int(img.shape[0] / 2), :, :].shape)
    ax[0,0].imshow(img[int(img.shape[0] / 2), :, :], cmap='gray')
    ax[0,1].imshow(img[:, int(img.shape[1] / 2), :], cmap='gray')
    ax[0,1].set_ylabel('Slice Number')
    ax[0,2].imshow(img[:, :, int(img.shape[2] / 2)], cmap='gray')
    ax[0,2].set_ylabel('Slice Number')
    ax[0,0].imshow(msk_img[int(msk_img.shape[0] / 2), :, :], cmap='jet', alpha=0.2)
    ax[0,1].imshow(msk_img[:, int(msk_img.shape[1] / 2), :], cmap='jet', alpha=0.2)
    ax[0,2].imshow(msk_img[:, :, int(msk_img.shape[2] / 2)], cmap='jet', alpha=0.2)

    ax[0,1].set_aspect(spacing[2] / spacing[0])
    ax[0, 2].set_aspect(spacing[2] / spacing[0])
    first_slice=0
    last_slice = msk_img.shape[0]
    for i in range(last_slice):
        if np.max(msk_img[i,:,:]) >= 1:
            first_slice = i
            break

    for i in reversed(range(last_slice)):
        if np.max(msk_img[i,:,:]) >= 1:
            last_slice = i
            break

    print(first_slice, last_slice)
    for i, slice in enumerate(range(first_slice, last_slice+1,(last_slice-first_slice)/(num_slices-1))):

        ax[1, i].imshow(img[slice, :, :], cmap='gray')
        ax[1, i].imshow(msk_img[slice, :, :], cmap='jet', alpha=0.2)
        ax[1, i].set_title('Slice Number {}'.format(slice))

    if None is not save_file:
        print('Saving ',save_file)
        plt.savefig(save_file)

def flip_and_save( nrrd_file, axis = 0, create_backup=True ):

    if create_backup:
        file, ext = os.path.splitext(nrrd_file)
        shutil.copy2(nrrd_file, file+'_bkup'+ext )

    nrrd_reader = sitk.ImageFileReader()
    nrrd_reader.SetFileName(nrrd_file)
    img_sitk = nrrd_reader.Execute()
    img = sitk.GetArrayFromImage(img_sitk)
    img = (np.flip(img, axis))
    nrrd_writer = sitk.ImageFileWriter()
    simg = sitk.GetImageFromArray(img)
    simg.SetSpacing(img_sitk.GetSpacing())
    nrrd_writer.SetFileName(nrrd_file)
    nrrd_writer.SetUseCompression(True)
    nrrd_writer.Execute(simg)




if __name__ == "__main__":




    names = ['AO21991VE.R','AS15605YE.R','GU04817JG.R','IP13348RH.R','KG93381SY.R','PX90332IE.R']

    dir = "C:\Users\Gregory\OneDrive - UHN\Projects\JDMI-AI\CAC-Scoring\Kate_Segmentations\\flipcheck"
    name ="GU04817JG.R.nrrd"
    #flip_and_save(os.path.join(dir,name))

    save_fig_filename = None
    for name in names:
        flip = True
        filename_img = os.path.join(dir, name+'.h5')
        filename_msk = os.path.join(dir, name+'.nrrd')

        save_fig_filename = None

        if flip:
            save_fig_filename = os.path.join(dir, 'flipped_'+name+'.png')
        else:
            save_fig_filename = os.path.join(dir, name+'.png')
        h5py_data = h5py.File(filename_img, 'r', swmr=True)

        img = np.flip(np.transpose(h5py_data['img'][0], (2, 0, 1)), axis=0)

        nrrd_reader = sitk.ImageFileReader()

        nrrd_reader.SetFileName(filename_msk)
        msk_sitk = nrrd_reader.Execute()
        print("{} : Direction {}, keys {}".format(name, msk_sitk.GetDirection(),msk_sitk.GetMetaDataKeys()))
        for key in msk_sitk.GetMetaDataKeys():
            print("{}: {}".format(key, msk_sitk.GetMetaData(key)))
        #dir = np.array(msk_sitk.GetDirecition()


        sp = msk_sitk.GetSpacing()
        #if 'GU' in name:
        #    flip = False

        if flip:
            """
            
            msk_img_rot = (np.flip(msk_img, 0))
            """
            msk_sitk = sitk.Flip(msk_sitk, [False, False, True])
            msk_img_rot = sitk.GetArrayFromImage(msk_sitk)
            plot_im(img, msk_img_rot, sp, '{} Flipped'.format(name),save_fig_filename)
        else:
            msk_img = sitk.GetArrayFromImage(msk_sitk)
            plot_im(img, msk_img, sp, '{} Original'.format(name), save_fig_filename)

    """
    fig, ax = plt.subplots(2,3)
    ax[0][0].imshow(msk_img[int(msk_img.shape[0] / 2), :, :], cmap='gray')
    ax[0][1].imshow(msk_img[:, int(msk_img.shape[1] / 2), :], cmap='gray')
    ax[0][2].imshow(msk_img[:, :, int(msk_img.shape[2] / 2)], cmap='gray')
    ax[1][0].imshow(img[int(img.shape[0] / 2), :, :], cmap='gray')
    ax[1][1].imshow(img[:, int(img.shape[1] / 2), :], cmap='gray')
    ax[1][2].imshow(img[:, :, int(img.shape[2] / 2)], cmap='gray')
    plt.show()
    """



    """
    fig, ax = plt.subplots(1)
    ax.imshow(img[int(img.shape[0] / 2), :, :], cmap='gray')
    ax.imshow(msk_img[int(msk_img.shape[0] / 2), :, :], cmap='jet', alpha=0.5)

    fig, ax = plt.subplots(1)
    ax.imshow(img[:, int(img.shape[1] / 2), :], cmap='gray')
    ax.imshow(msk_img[:, int(msk_img.shape[1] / 2), :], cmap='jet', alpha=0.5)
    """
    #ax.set_aspect(

    plt.show()
    # img = h5py_data['img'][0,...]
    # img = np.rot90(img, k=1, axes=(0,2)) #rotate 90 around y
    # img = np.rot90(img, k=-1, axes=(1,2)) #rotate -90 around x
    # img_sitk = sitk.GetImageFromArray(img)

    # equivelant
    # or img_sitk = sitk.GetImageFromArray(transpose(img,(1,2,0))) #untested

    # original
    img_sitk = sitk.GetImageFromArray(np.flip(np.transpose(h5py_data['img'][0], (2, 0, 1)), axis=0))
