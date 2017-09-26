import numpy as np
from osgeo import gdal
from scipy import ndimage as ndi
from skimage import morphology
from skimage.draw import line

def rgb2gray(rgb):
    return (rgb[0, :, ]+rgb[1, :, ]+rgb[2, :, ]+rgb[3, :, ]+rgb[4, :, ])/5.0

im1 = gdal.Open("image1.tif")
im2 = gdal.Open("image2.tif")

bands1=im1.ReadAsArray()
bands2=im2.ReadAsArray()

bands1=rgb2gray(bands1)
bands2=rgb2gray(bands2)

bands1=(bands1-np.amin(bands1))/(np.amax(bands1)-np.amin(bands1))
bands2=(bands2-np.amin(bands2))/(np.amax(bands2)-np.amin(bands2))

D = np.empty(bands1.shape)
D = np.divide(bands1, bands2)
B = D <= 0.57

def addline(x):
    rr, cc = line(0, 0, B.shape[0]-1, 0)
    B[rr, cc] = x
    rr, cc = line(B.shape[0]-1, 0, B.shape[0]-1, B.shape[0]-1)
    B[rr, cc] = x
    rr, cc = line(0, B.shape[0]-1, B.shape[0]-1, B.shape[0]-1)
    B[rr, cc] = x

addline(1)
B = ndi.binary_fill_holes(B)
addline(0)
cleaned=morphology.remove_small_objects(B,1200)

for i in range(5):
    cleaned = ndi.binary_dilation(cleaned)
cleaned = ndi.binary_fill_holes(cleaned)
for i in range(5):
    cleaned = ndi.binary_erosion(cleaned)

D = np.empty(bands1.shape)
D=np.true_divide(bands1,bands2)

labels = morphology.label(D)
labelCount = np.bincount(labels.ravel())
background = np.argmax(labelCount)
D[labels != background] = 1

B = D <= 0.57

B=morphology.remove_small_objects(B,1200)

G = np.empty(bands1.shape)
G=cleaned-B
G = ndi.binary_fill_holes(G)

G=morphology.remove_small_objects(G,1200)

#for i in range(5):
    #G = ndi.binary_dilation(G)
#G = ndi.binary_fill_holes(G)
#for i in range(5):
    #G = ndi.binary_erosion(G)

G=np.multiply(G,1)
sum=cleaned+G

def saveImage(image, outname, dsp):
    nrows, ncols = image.shape
    driv  = gdal.GetDriverByName('GTiff')
    dst = driv.Create(outname, ncols, nrows, 1, gdal.GDT_UInt16)
    dst.SetGeoTransform(dsp.GetGeoTransform())
    dst.SetProjection(dsp.GetProjection())
    dst.GetRasterBand(1).WriteArray(image)
    dst = None
    del dst

saveImage(sum,"test.tif", im1)