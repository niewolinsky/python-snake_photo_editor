import cv2
import numpy as np

def rotate_90_clockwise(imageCopyF):
    imageCopyF = cv2.rotate(imageCopyF, cv2.ROTATE_90_CLOCKWISE)
    return imageCopyF

def rotate_90_counterclockwise(imageCopyF):
    imageCopyF = cv2.rotate(imageCopyF, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return imageCopyF

def rotate_180(imageCopyF):
    imageCopyF = cv2.rotate(imageCopyF, cv2.ROTATE_180)
    return imageCopyF

def flip_vertical(imageCopyF):
    imageCopyF = cv2.flip(imageCopyF, 0)
    return imageCopyF

def flip_horizontal(imageCopyF):
    imageCopyF = cv2.flip(imageCopyF, 1)
    return imageCopyF

def scale(imageCopyF, scaleXF, scaleYF):
    (h1, w1) = imageCopyF.shape[:2]
    imageCopyF = cv2.resize(imageCopyF, (int(w1*scaleXF[0]), int(h1*scaleYF[0])))
    return imageCopyF