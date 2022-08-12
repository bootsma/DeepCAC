
import os
import numpy as np
import h5py
import csv
import SimpleITK as sitk
import matplotlib.pyplot as plt

if __name__ == "__main__":
    filename_img = 'C:\\Users\\Gregory\\OneDrive - UHN\\Projects\\JDMI-AI\\CAC-Scoring\\testseg\\CT_cadb05a4-c32f62f0-3500255a-8211bc48-be223c4c.h5'
    filename_msk = 'C:\\Users\\Gregory\\OneDrive - UHN\\Projects\\JDMI-AI\\CAC-Scoring\\testseg\\Segmentation.nrrd'
    h5py_data = h5py.File(filename_img, 'r', swmr=True)
    img = np.flip(np.transpose(h5py_data['img'][0], (2, 0, 1)), axis=0)

    nrrd_reader = sitk.ImageFileReader()

    nrrd_reader.SetFileName(filename_msk)
    msk_sitk = nrrd_reader.Execute()
    msk_img = sitk.GetArrayFromImage(msk_sitk)
    sp = msk_sitk.GetSpacing()
    fig, ax = plt.subplots(2,3)
    ax[0][0].imshow(msk_img[int(msk_img.shape[0] / 2), :, :], cmap='gray')
    ax[0][1].imshow(msk_img[:, int(msk_img.shape[1] / 2), :], cmap='gray')
    ax[0][2].imshow(msk_img[:, :, int(msk_img.shape[2] / 2)], cmap='gray')
    ax[1][0].imshow(img[int(img.shape[0] / 2), :, :], cmap='gray')
    ax[1][1].imshow(img[:, int(img.shape[1] / 2), :], cmap='gray')
    ax[1][2].imshow(img[:, :, int(img.shape[2] / 2)], cmap='gray')
    plt.show()

    fig, ax = plt.subplots(1, 3)
    ax[0].imshow(img[int(img.shape[0] / 2), :, :], cmap='gray')
    ax[1].imshow(img[:, int(img.shape[1] / 2), :], cmap='gray')
    ax[2].imshow(img[:, :, int(img.shape[2] / 2)], cmap='gray')
    ax[0].imshow(msk_img[int(msk_img.shape[0] / 2), :, :], cmap='jet', alpha=0.5)
    ax[1].imshow(msk_img[:, int(msk_img.shape[1] / 2), :], cmap='jet', alpha=0.5)
    ax[2].imshow(msk_img[:, :, int(msk_img.shape[2] / 2)], cmap='jet', alpha=0.5)

    ax[1].set_aspect(sp[2] / sp[0])
    ax[2].set_aspect(sp[2] / sp[0])

    fig, ax = plt.subplots(1)
    ax.imshow(img[int(img.shape[0] / 2), :, :], cmap='gray')
    ax.imshow(msk_img[int(msk_img.shape[0] / 2), :, :], cmap='jet', alpha=0.5)

    fig, ax = plt.subplots(1)
    ax.imshow(img[:, int(img.shape[1] / 2), :], cmap='gray')
    ax.imshow(msk_img[:, int(msk_img.shape[1] / 2), :], cmap='jet', alpha=0.5)

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
