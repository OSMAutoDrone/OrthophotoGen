from typing import NamedTuple
import math
import os
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import json
import argparse

#

calibimagesfolder = "CalibrationImages"
testMode = True


class BoardDetectionResults(NamedTuple):
    charuco_corners: np.ndarray
    charuco_ids: np.ndarray
    aruco_corners: np.ndarray
    aruco_ids: np.ndarray


class PointReferences(NamedTuple):
    object_points: np.ndarray
    image_points: np.ndarray


class CameraCalibrationResults(NamedTuple):
    repError: float
    camMatrix: np.ndarray
    distcoeff: np.ndarray
    rvecs: np.ndarray
    tvecs: np.ndarray

#default values
def_SQUARE_LENGTH = 500 #size of squares in mm??
def_MARKER_LENGHT = 300 #size of squares in mm??
def_NUMBER_OF_SQUARES_VERTICALLY = 11  #number of squares
def_NUMBER_OF_SQUARES_HORIZONTALLY = 8 #number of squares


def generate_charuco_board(square_length, marker_lenght, number_of_squares_vertically, number_of_squares_horizontally):
    #generate the charuco board
    charuco_marker_dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)
    charuco_board = cv.aruco.CharucoBoard(
        size=(number_of_squares_horizontally, number_of_squares_vertically),
        squareLength=square_length,
        markerLength=marker_lenght,
        dictionary=charuco_marker_dictionary
        )
    #save the charuco board for printing
    image_name = f'ChArUco_Marker_{number_of_squares_horizontally}x{number_of_squares_vertically}.png'
    charuco_board_image = charuco_board.generateImage(
            [i*square_length
            for i in (number_of_squares_horizontally, number_of_squares_vertically)]
    )
    cv.imwrite(image_name, charuco_board_image)

    return charuco_board, charuco_board_image


def plot_results(img_bgr, detection_results, point_references, charuco_board_image):
    fig, axes = plt.subplots(2, 2)
    axes = axes.flatten()
    img_rgb = cv.cvtColor(img_bgr, cv.COLOR_BGR2RGB)
    axes[0].imshow(img_rgb)
    axes[0].axis("off")

    axes[1].imshow(img_rgb)
    axes[1].axis("off")
    axes[1].scatter(
        np.array(detection_results.aruco_corners).squeeze().reshape(-1, 2)[:, 0],
        np.array(detection_results.aruco_corners).squeeze().reshape(-1, 2)[:, 1],
        s=5,
        c="green",
        marker="x",
    )
    axes[2].imshow(img_rgb)
    axes[2].axis("off")

    axes[2].scatter(
        detection_results.charuco_corners.squeeze()[:, 0],
        detection_results.charuco_corners.squeeze()[:, 1],
        s=20,
        edgecolors="red",
        marker="o",
        facecolors="none"
    )
    axes[3].imshow(cv.cvtColor(charuco_board_image, cv.COLOR_BGR2RGB))
    axes[3].scatter(
        point_references.object_points.squeeze()[:, 0],
        point_references.object_points.squeeze()[:, 1]
    )
    fig.tight_layout()
    fig.savefig("test.png", dpi=900)
    plt.show()

def shapeVectors(detection_results, point_references):
    np.array(detection_results.aruco_corners).squeeze().reshape(-1, 2)[:, 0]
    np.array(detection_results.aruco_corners).squeeze().reshape(-1, 2)[:, 1]
    detection_results.charuco_corners.squeeze()[:, 0]
    detection_results.charuco_corners.squeeze()[:, 1]
    point_references.object_points.squeeze()[:, 0]
    point_references.object_points.squeeze()[:, 1]

    

def create_point_cloud(calibration_images, charuco_board, charuco_board_image):
    global args
    total_object_points = []
    total_image_points = []
    for img_bgr in calibration_images:
        img_gray = cv.cvtColor(img_bgr, cv.COLOR_BGR2GRAY)
        charuco_detector = cv.aruco.CharucoDetector(charuco_board)
        detection_results = BoardDetectionResults(*charuco_detector.detectBoard(img_gray))

        point_references = PointReferences(
            *charuco_board.matchImagePoints(
                detection_results.charuco_corners,
                detection_results.charuco_ids
            )
        )
        if args.PR:
            plot_results(
            img_bgr,
            detection_results,
            point_references,
            charuco_board_image
            )
        else:
            shapeVectors(detection_results, point_references)

        total_object_points.append(point_references.object_points)
        total_image_points.append(point_references.image_points)
        imgShape = img_gray.shape


    return total_image_points, total_object_points, imgShape


#load all images in folder
def load_images_from_folder(folder):
    images = []
     
    #load images from folder
    for filename in os.listdir(folder):
        img = cv.imread(os.path.join(folder,filename))
        if img is not None:
            #img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
            images.append(img)
 
    return images


def parseArgs():
    parser = argparse.ArgumentParser(description="Camera Calibration extractor")
    parser.add_argument("--CIF", default="CalibrationImages", help="Calibration Image Folder")
    parser.add_argument("--CFN", default="CameraParams", help="Name of the output parameters file")
    parser.add_argument("--CBP", default=[500,300,11,8], help="[square_length, marker_lenght, number_of_squares_vertically, number_of_squares_horizontally]")
    parser.add_argument("--PR", action="store_true", default=False, help="Plot Results")
    #parser.add_argument("", default="")
    
    args = parser.parse_args()
    return args

if __name__=="__main__":
    global args 
    args = parseArgs()
    
    #generate charuco board
    charuco_board, charuco_board_image = generate_charuco_board(args.CBP[0],args.CBP[1],args.CBP[2],args.CBP[3])

    # load or create images for calibration
    calibration_images = load_images_from_folder(calibimagesfolder) #TODO test function and image read in folder
    
    #create the point cloud for the calibration
    total_image_points, total_object_points, imgShape = create_point_cloud(calibration_images, charuco_board, charuco_board_image)

    #do calibration and save in Result object
    calibration_results = CameraCalibrationResults(
        *cv.calibrateCamera(
            total_object_points,
            total_image_points,
            imgShape,
            None,
            None
        )
    )

    #save calibration parameters to be reused in other calibration script
    np.savez("camera.calib", 
            repError=calibration_results.repError,
            camMatrix=calibration_results.camMatrix,
            distcoeff=calibration_results.distcoeff,
            rvecs=calibration_results.rvecs,
            tvecs=calibration_results.tvecs)