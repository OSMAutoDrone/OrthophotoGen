# Source - https://stackoverflow.com/a
# Posted by m.ariuz, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-29, License - CC BY-SA 4.0

from typing import NamedTuple
import math

import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import json

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


SQUARE_LENGTH = 500
MARKER_LENGHT = 300
NUMBER_OF_SQUARES_VERTICALLY = 11
NUMBER_OF_SQUARES_HORIZONTALLY = 8

charuco_marker_dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)
charuco_board = cv.aruco.CharucoBoard(
size=(NUMBER_OF_SQUARES_HORIZONTALLY, NUMBER_OF_SQUARES_VERTICALLY),
squareLength=SQUARE_LENGTH,
markerLength=MARKER_LENGHT,
dictionary=charuco_marker_dictionary
)

image_name = f'ChArUco_Marker_{NUMBER_OF_SQUARES_HORIZONTALLY}x{NUMBER_OF_SQUARES_VERTICALLY}.png'
charuco_board_image = charuco_board.generateImage(
        [i*SQUARE_LENGTH
         for i in (NUMBER_OF_SQUARES_HORIZONTALLY, NUMBER_OF_SQUARES_VERTICALLY)]
)
cv.imwrite(image_name, charuco_board_image)


def plot_results(image_of_board, original_board, detection_results, point_references):
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


def generate_test_images(image):
    """Use random homograpy.

    -> Just to test detection. This doesn't simulate a perspective
    projection of one single camera! (Intrinsics change randomly.)
    For a "camera simulation" one would need to define fixed intrinsics
    and random extrinsics. Then cobine them into a projective matrix.
    And apply this to the Image. -> Also you need to add a random z
    coordinate to the image, since a projection is from 3d space into 2d
    space.
    """
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


def display_images(images):
    N = len(images)
    cols = math.ceil(math.sqrt(N))
    rows = math.ceil(N / cols)

    for i, img in enumerate(images):
        plt.subplot(rows, cols, i + 1)
        plt.imshow(img, cmap='gray')
        plt.axis('off')
    plt.tight_layout()
    plt.show()


# Create N test images based on the originaly created pattern.
N = 3
random_images = []
charuco_board_image = cv.cvtColor(charuco_board_image, cv.COLOR_GRAY2BGR)
for _ in range(N):
    random_images.append(generate_test_images(charuco_board_image))
#display_images(random_images)


total_object_points = []
total_image_points = []
for img_bgr in random_images:
    img_gray = cv.cvtColor(img_bgr, cv.COLOR_BGR2GRAY)
    charuco_detector = cv.aruco.CharucoDetector(charuco_board)
    detection_results = BoardDetectionResults(*charuco_detector.detectBoard(img_gray))

    point_references = PointReferences(
        *charuco_board.matchImagePoints(
            detection_results.charuco_corners,
            detection_results.charuco_ids
        )
    )
    plot_results(
       img_gray,
       charuco_board_image,
       detection_results,
       point_references
    )
    total_object_points.append(point_references.object_points)
    total_image_points.append(point_references.image_points)


calibration_results = CameraCalibrationResults(
   *cv.calibrateCamera(
       total_object_points,
       total_image_points,
       img_gray.shape,
       None,
       None
   )
)

np.savez("test.calib", 
         repError=calibration_results.repError,
         camMatrix=calibration_results.camMatrix,
         distcoeff=calibration_results.distcoeff,
         rvecs=calibration_results.rvecs,
         tvecs=calibration_results.tvecs)

