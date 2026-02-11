import numpy as np
from typing import NamedTuple
import cv2 as cv
import os

class CameraCalibrationResults(NamedTuple):
    repError: float   #not needed for undistort
    camMatrix: np.ndarray
    distcoeff: np.ndarray
    rvecs: np.ndarray #not needed for undistort
    tvecs: np.ndarray #not needed for undistort

def load_images_from_folder(folder):
    images = []
        
    #load images from folder
    for filename in os.listdir(folder):
        img = cv.imread(os.path.join(folder,filename))
        if img is not None:
            #img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
            images.append(img)

    return images



calibparam = np.load("camera.calib.npz")

calib_params = CameraCalibrationResults(
    repError = calibparam["repError"],
    camMatrix = calibparam["camMatrix"],
    distcoeff = calibparam["distcoeff"][0],
    rvecs = calibparam["rvecs"],
    tvecs = calibparam["tvecs"])

imgs = load_images_from_folder("Input")

for img in imgs:
    h,  w = img.shape[:2]
    #newcameramtx, roi = cv.getOptimalNewCameraMatrix(calib_params.camMatrix, calib_params.distcoeff, (w,h), 1, (w,h)) #crée un bord noir, est-ce que cette fonction est nécessaire?
    undist = cv.undistort(img, calib_params.camMatrix, calib_params.distcoeff, None)
    imageName = "Output/imagetest.png"
    cv.imwrite(imageName, undist)


