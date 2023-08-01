import numpy as np
import cv2

# Load calibration data
with np.load('calibration_data_npz.npz') as data:
    K = data['K']
    D = data['D']

# Load an image
img = cv2.imread('test_image.jpg')

# Undistort the image
h, w = img.shape[:2]
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (w,h), cv2.CV_16SC2)
undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

# Save the undistorted image
cv2.imwrite('yellowwihtpiecesonthem.jpg', undistorted_img)
