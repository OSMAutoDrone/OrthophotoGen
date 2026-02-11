from typing import NamedTuple
import math
import os
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import json
import argparse

"""Use random homograpy.

-> Just to test detection. This doesn't simulate a perspective
projection of one single camera! (Intrinsics change randomly.)
For a "camera simulation" one would need to define fixed intrinsics
and random extrinsics. Then cobine them into a projective matrix.
And apply this to the Image. -> Also you need to add a random z
coordinate to the image, since a projection is from 3d space into 2d
space.
"""
def generate_test_images(image):
    h, w = image.shape[:2]
    src_points = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst_points = np.float32([
        [np.random.uniform(w * -0.2, w * 0.2), np.random.uniform(0, h * 0.2)],
        [np.random.uniform(w * 0.8, w*1.2), np.random.uniform(0, h * 0.6)],
        [np.random.uniform(w * 0.8, w), np.random.uniform(h * 0.8, h)],
        [np.random.uniform(0, w * 0.2), np.random.uniform(h * 0.8, h*1.5)]
    ])
    homography_matrix, _ = cv.findHomography(src_points, dst_points)
    image_projected = cv.warpPerspective(image, homography_matrix, (w, h))
    return image_projected


def generate_charuco_board(square_length, marker_lenght, number_of_squares_vertically, number_of_squares_horizontally, imagePath):
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
    image_name = imagePath + "/src/"+ image_name
    charuco_board_image = charuco_board.generateImage(
            [i*square_length
            for i in (number_of_squares_horizontally, number_of_squares_vertically)]
    )
    cv.imwrite(image_name, charuco_board_image)

    return charuco_board, charuco_board_image


def distort_image(img):
    h, w = img.shape[:2]

    # 2. Define camera matrix (intrinsic parameters)
    # Assuming principal point is at the center
    focal_length = max(h, w)
    K = np.array([
        [focal_length, 0, w / 2],
        [0, focal_length, h / 2],
        [0, 0, 1]
    ], dtype=np.float32)

    # 3. Define distortion coefficients (radial and tangential)
    # Positive k1, k2 give pincushion distortion; negative give barrel distortion
    k1 = -0.2 # Adjust this value to control distortion strength
    k2 = -0.1
    p1 = 0.0
    p2 = 0.0
    k3 = 0.0
    D = np.array([k1, k2, p1, p2, k3], dtype=np.float32)


    pts_distort = []
    for y in range(h):
        for x in range(w):
            pts_distort.append([x, y])
    
    pts_distort = np.array(pts_distort, dtype=np.float32)

    # Use cv.undistortPoints to find the corresponding source (undistorted) coordinates
    # R is identity matrix, P is the new camera matrix (can be same as original K)
    pts_ud = cv.undistortPoints(pts_distort, K, D, P=K)
    
    # Reshape the points and create the x and y mapping arrays
    map_x = pts_ud[:, 0, 0].reshape((h, w)).astype(np.float32)
    map_y = pts_ud[:, 0, 1].reshape((h, w)).astype(np.float32)
    
    # Apply the remap operation
    distorted_image = cv.remap(img, map_x, map_y, cv.INTER_LINEAR)
    
    return distorted_image


N = 3
#default values
def_SQUARE_LENGTH = 500 #size of squares in m??
def_MARKER_LENGHT = 300 #size of squares in m??
def_NUMBER_OF_SQUARES_VERTICALLY = 11  #number of squares
def_NUMBER_OF_SQUARES_HORIZONTALLY = 8 #number of squares
imagePath = "CalibrationImages"
charuco_board, charuco_board_image = generate_charuco_board(def_SQUARE_LENGTH, def_MARKER_LENGHT, def_NUMBER_OF_SQUARES_VERTICALLY, def_NUMBER_OF_SQUARES_HORIZONTALLY, imagePath)
charuco_board_image = cv.cvtColor(charuco_board_image, cv.COLOR_GRAY2BGR)
for i in range(N):
    imgName = imagePath +"/image_"+ str(i)+".png"
    #img = generate_test_images(charuco_board_image)
    img = distort_image(charuco_board_image)
    cv.imwrite(imgName, img)


