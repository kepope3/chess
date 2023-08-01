import cv2
import numpy as np

# Read the image
image = cv2.imread('./camcalib/undistorted_image2.jpg')

# Specify the crop dimensions (x, y, w, h)
crop_rectangle = (90, 0, 440, 450)
x, y, w, h = crop_rectangle

# Crop the image
cropped_image = image[y:y+h, x:x+w]

# Convert to grayscale
gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

bilateral_filtered_image = cv2.bilateralFilter(gray, 5, 75, 75)

# Apply Gaussian blur to reduce noise and avoid false circle detection
gray_blur = cv2.GaussianBlur(bilateral_filtered_image, (15, 15), 0)

# Threshold the gray image to get only darker colors
_, threshold = cv2.threshold(gray_blur, 50, 255, cv2.THRESH_BINARY_INV)

# Define the grid dimensions
grid_size = 8

# Calculate the step size
step_size_x = w // grid_size
step_size_y = h // grid_size

# Draw the grid and check for chess pieces
for i in range(0, w, step_size_x):
    for j in range(0, h, step_size_y):
        # Extract the cell
        cell = threshold[j:j+step_size_y, i:i+step_size_x]

        # Calculate the proportion of dark pixels
        white_pixels = np.sum(cell == 0)
        total_pixels = np.size(cell)
        if white_pixels / total_pixels < 0.7:  
            cv2.rectangle(cropped_image, (i, j), (i+step_size_x, j+step_size_y), (0, 0, 255), 2)

    cv2.line(threshold, (i, 0), (i, h), (0, 255, 0), 1)

for i in range(0, h, step_size_y):
    cv2.line(threshold, (0, i), (w, i), (0, 255, 0), 1)

#display threshold image
cv2.imshow("threshold image", threshold)
cv2.waitKey(0)

# Display the cropped image
cv2.imshow('Cropped and Gridded Image', cropped_image)
cv2.waitKey(0)

# Save the cropped image
cv2.imwrite('output.jpg', cropped_image)

# Close all windows
cv2.destroyAllWindows()
