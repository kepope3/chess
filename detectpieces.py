import cv2
import numpy as np

# Read the image
image = cv2.imread('./camcalib/undistorted_image.jpg')

# Specify the crop dimensions (x, y, w, h)
crop_rectangle = (90, 0, 440, 450)
x, y, w, h = crop_rectangle

# Crop the image
cropped_image = image[y:y+h, x:x+w]

# Convert to HSV for better color isolation
hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

# Define color range for red pieces (remember HSV color space is different!)
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 50, 50])
upper_red2 = np.array([180, 255, 255])

# Threshold the HSV image to get only red colors
red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)

# Combine the two masks
red_mask = cv2.bitwise_or(red_mask1, red_mask2)
# Define the grid dimensions
grid_size = 8

# Calculate the step size
step_size_x = w // grid_size
step_size_y = h // grid_size

# Draw the grid and check for red pieces
for i in range(0, w, step_size_x):
    for j in range(0, h, step_size_y):
        # Extract the cell
        cell = red_mask[j:j+step_size_y, i:i+step_size_x]

        # Calculate the proportion of red pixels
        red_pixels = np.sum(cell == 255)
        total_pixels = np.size(cell)
        if red_pixels / total_pixels > 0.020:  # Modify this threshold based on your specific needs
            cv2.rectangle(cropped_image, (i, j), (i+step_size_x, j+step_size_y), (0, 0, 255), 2)

    cv2.line(red_mask, (i, 0), (i, h), (0, 255, 0), 1)

for i in range(0, h, step_size_y):
    cv2.line(red_mask, (0, i), (w, i), (0, 255, 0), 1)

#display red mask image
cv2.imshow("Red mask", red_mask)
cv2.waitKey(0)

# Display the cropped image
cv2.imshow('Cropped and Gridded Image', cropped_image)
cv2.waitKey(0)

# Save the cropped image
cv2.imwrite('output.jpg', cropped_image)

# Close all windows
cv2.destroyAllWindows()
