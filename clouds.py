import numpy as np
from osgeo import gdal
import skimage.color as color
from skimage import morphology
import os

def saveImage(image, outname, dsp):
    nrows, ncols = image.shape
    driv  = gdal.GetDriverByName('GTiff')
    dst = driv.Create(outname, ncols, nrows, 1, gdal.GDT_UInt16)
    dst.SetGeoTransform(dsp.GetGeoTransform())
    dst.SetProjection(dsp.GetProjection())
    dst.GetRasterBand(1).WriteArray(image)
    dst = None
    del dst

def mask(threshold_binary, file, threshold_small):
    bands=file.ReadAsArray()
    bands=np.true_divide(bands-np.amin(bands),np.amax(bands)-np.amin(bands))
    red = bands[0]
    green = bands[1]
    blue = bands[2]
    nir = bands[4]

    rgb = np.empty((red.shape[0], red.shape[1], 3))
    rgb[:, :, 0] = red
    rgb[:, :, 1] = green
    rgb[:, :, 2] = blue
    hsv=color.rgb2hsv(rgb)

    x = (hsv[:, :, 2] - hsv[:, :, 1]) * nir

    B = x <= threshold_binary
    B=~B
    B=morphology.remove_small_objects(B,threshold_small)
    return B

path='/home/sinegaa/1055526/'
files=[]
filenames=[]
for filename in os.listdir(path):
    files.append(gdal.Open(path+filename))
    filenames.append(filename)

for i in range(len(files)):
    B=mask(0.11, files[i], 15000)
    if (B.any()==True):
        B1 = mask(0.05, files[i], 300)
        saveImage(B1, filenames[i].replace('.tif', '_clouds') + '.tif', files[i])