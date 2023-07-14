import cv2
import numpy as np
import time

PATTERN_SIZE = (7, 7)

# Piece class


class Piece:
    def __init__(self, name, lower_color, upper_color, position=None):
        self.name = name
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.position = position


# Define the pieces and their color ranges
pieces = [
    Piece("WHITE KING (Red)", np.array([0, 70, 50]), np.array(
        [10, 255, 255])),
    Piece("WHITE QUEEN (Pink)", np.array([160, 70, 255]), np.array(
        [180, 255, 255])),
    Piece("WHITE BISHOP (Yellow)", np.array([20, 70, 255]), np.array(
        [40, 255, 255])),
    Piece("WHITE KNIGHT GREEN", np.array([60, 70, 255]), np.array(
        [80, 255, 255])),
    Piece("WHITE ROOK BLUE", np.array([90, 70, 255]), np.array(
        [110, 255, 255])),
    Piece("WHITE PAWN GOLD", np.array([20, 100, 255]), np.array(
        [30, 255, 255])),
    Piece("BLACK KING LIME", np.array([35, 70, 255]), np.array(
        [55, 255, 255])),
    Piece("BLACK QUEEN BROWN", np.array([10, 70, 75]), np.array(
        [30, 255, 255])),
    Piece("BLACK BISHOP GREY", np.array([80, 70, 150]), np.array(
        [100, 255, 255])),
    Piece("BLACK KNIGHT PURPLE", np.array([120, 70, 255]), np.array(
        [140, 255, 255])),
    Piece("BLACK ROOK ORANGE", np.array([5, 70, 255]), np.array(
        [25, 255, 255])),
    Piece("BLACK PAWN LAVANDER", np.array([125, 70, 255]), np.array(
        [145, 255, 255]))
]


def findSquares(corners, pattern_size, image):

    # Get the bounding rectangle around the chessboard
    x_min = int(np.min(corners[:, :, 0]))
    y_min = int(np.min(corners[:, :, 1]))
    x_max = int(np.max(corners[:, :, 0]))
    y_max = int(np.max(corners[:, :, 1]))

    # Calculate the width and height of each square
    # subtract 1 because 7 squares will have 6 gaps
    square_width = (x_max - x_min) / (pattern_size[0] - 1)
    square_height = (y_max - y_min) / (pattern_size[1] - 1)

    # Adjust the bounding rectangle to include the outer squares
    x_min -= int(square_width)
    y_min -= int(square_height)
    x_max += int(square_width)
    y_max += int(square_height)

    # Check that the adjusted coordinates are within the image boundaries
    x_min = max(x_min, 0)
    y_min = max(y_min, 0)
    x_max = min(x_max, image.shape[1])
    y_max = min(y_max, image.shape[0])

    # Draw the adjusted bounding rectangle
    # cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 0), 2)

    # Store the individual square positions
    square_positions = []
    for i in range(8):
        for j in range(8):
            top_left = (x_min + int(square_width * j),
                        y_min + int(square_height * i))
            bottom_right = (x_min + int(square_width * (j + 1)),
                            y_min + int(square_height * (i + 1)))
            square_positions.append((top_left, bottom_right))

            # Draw the individual squares
            # cv2.rectangle(image, top_left, bottom_right, (0, 0, 0), 1)
            # Draw the traditional chess coordinates
            # 'a' is ASCII 97 and '1' is ASCII 49, hence using them for respective axes
            # coord = chr(97 + j) + str(8 - i)
            # cv2.putText(image, coord, (top_left[0] + 5, top_left[1] + 25), cv2.FONT_HERSHEY_SIMPLEX,
            #             0.7, (0, 0, 0), 2)

    return square_positions


def getChessboard():
    # Load the chessboard image
    image = cv2.imread("chessboard.jpg")

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Define the chessboard pattern size

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCornersSB(
        gray, PATTERN_SIZE, flags=cv2.CALIB_CB_EXHAUSTIVE)

    return ret, corners, image


def detectPiece(piece, square_positions, hsv):
    piece_mask = cv2.inRange(hsv, piece.lower_color, piece.upper_color)
    piece_contours, _ = cv2.findContours(
        piece_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if len(piece_contours) > 0:
        largest_contour = max(piece_contours, key=cv2.contourArea)
        piece_moments = cv2.moments(largest_contour)

        # Check if the moment area is non-zero
        if piece_moments["m00"] != 0:
            piece_centroid_x = int(piece_moments["m10"] / piece_moments["m00"])
            piece_centroid_y = int(piece_moments["m01"] / piece_moments["m00"])

            for i in range(8):
                for j in range(8):
                    top_left, bottom_right = square_positions[i * 8 + j]
                    if (
                        top_left[0] <= piece_centroid_x < bottom_right[0]
                        and top_left[1] <= piece_centroid_y < bottom_right[1]
                    ):
                        return f"{chr(97 + j)}{8 - i}"

    return None


while True:

    ret, corners, image = getChessboard()

    if ret:
        square_positions = findSquares(corners, PATTERN_SIZE, image)

        # cv2.imshow("Detected Chessboard", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Convert the image to HSV for color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        for piece in pieces:
            position = detectPiece(piece, square_positions, hsv)

            if position:
                piece.position = position
                print(f"{piece.name} is on: {piece.position}")

    else:
        print("Chessboard not found.")

    time.sleep(1)
