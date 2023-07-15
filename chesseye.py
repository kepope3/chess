import cv2
import numpy as np
import time
import chess
import chess.engine

PATTERN_SIZE = (7, 7)
RED_LOWER_COLOR = np.array([0, 70, 50])
RED_UPPER_COLOR = np.array([10, 255, 255])
INIT_BOARD_SETUP = ['PPPPPPPP', 'PPPPPPPP', '........', '........', '........', '........', 'PPPPPPPP', 'PPPPPPPP']

is_board_setup = None

def find_squares(corners, pattern_size, image):

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


def get_chessboard():
    # Load the chessboard image
    image = cv2.imread("chessboard.jpg")

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Define the chessboard pattern size

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCornersSB(
        gray, PATTERN_SIZE, flags=cv2.CALIB_CB_EXHAUSTIVE)

    return ret, corners, image

def detect_pieces(hsv):
    # Create an empty 8x8 board
    virtual_board = [['.' for _ in range(8)] for _ in range(8)]

    # Get a binary mask where red pieces are white and everything else is black
    piece_mask = cv2.inRange(hsv, RED_LOWER_COLOR, RED_UPPER_COLOR)

    # Iterate over each square on the chessboard image
    for i in range(8):
        for j in range(8):
            top_left, bottom_right = square_positions[i * 8 + j]

            # Extract the square's region from the binary mask
            square_mask = piece_mask[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

            # If the square contains any white pixels, mark it as containing a red piece
            if np.any(square_mask):
                virtual_board[i][j] = 'P'

    return virtual_board

def print_board(board):
    for row in board:
        print(' '.join(row))


def has_board_been_setup(vboard, is_board_setup):
    if is_board_setup is None:
        vboard_str = [[str(piece) for piece in row] for row in vboard]
        board_init_setup_str = [[str(piece) for piece in row] for row in INIT_BOARD_SETUP]

        if  vboard_str == board_init_setup_str:
             return True
            
def make_move(vboard, cached_board, lib_board):
    vboard_str = [[str(piece) for piece in row] for row in vboard]
    cached_str = [[str(piece) for piece in row] for row in cached_board]

    if vboard_str != cached_str:
        changes = 0

        for j in range(8):
            for i in range(8):
                if cached_str[j][i] != vboard_str[j][i]:
                    changes += 1  # Increment changes if a difference is detected

        first_change = None
        second_change = None

        if changes == 1:
            print(board)
        
        if changes == 2:
            for i in range(8):
                for j in range(8):
                    if first_change is None and cached_str[i][j] != vboard_str[i][j]:
                        first_change = chess.square(j, 7-i) # 7-i because the chess board's rank is from 8 to 1, top to bottom
                    elif second_change is None and cached_str[i][j] != vboard_str[i][j]:
                        second_change = chess.square(j, 7-i)
                    else:
                        continue                            
            try:
                first_possible_move = chess.Move.from_uci(chess.square_name(first_change) + chess.square_name(second_change))
                second_possible_move = chess.Move.from_uci(chess.square_name(second_change) + chess.square_name(first_change))
            except Exception:
                print("Illegal move, ensure when capturing to lift both pieces")
                print("Put pieces back!")
                print (board)
                return cached_board
            

            if lib_board.is_legal(first_possible_move):
                lib_board.push(first_possible_move)
                print("A piece moved from " + chess.square_name(first_change) + " to " + chess.square_name(second_change))
                # Change the piece at the destination square
                vboard[7 - chess.square_rank(second_change)][chess.square_file(second_change)] = 'P'  # chess.square_rank() and chess.square_file() gives rank and file of a square respectively.
                return vboard.copy()  # Update cached board
            elif lib_board.is_legal(second_possible_move):
                lib_board.push(second_possible_move)
                print("A piece moved from " + chess.square_name(second_change) + " to " + chess.square_name(first_change))
                # Change the piece at the destination square
                vboard[7 - chess.square_rank(first_change)][chess.square_file(first_change)] = 'P'
                return vboard.copy()  # Update cached board
            else:
                print("Illegal moves, put pieces back!")
                print (board)

    return cached_board


def board_to_fen(board):
    # Use join function to concatenate list elements into string
    fen = '/'.join(board)
    # Add the additional FEN fields
    fen += " w KQkq - 0 1"
    return fen

engine = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-windows-x86-64-avx2.exe")
board = chess.Board()
cached_board = None

while True:
    ret, corners, image = get_chessboard()

    if ret:
        square_positions = find_squares(corners, PATTERN_SIZE, image)
     
        if board.turn == chess.BLACK:
            engine.configure({"Skill Level": 1})
            result = engine.play(board, chess.engine.Limit(time=.1))
            print(result.move)
        # cv2.imshow("Detected Chessboard", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Convert the image to HSV for color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        vboard = detect_pieces(hsv)        

        #init setup
        if cached_board is None:
            is_board_setup = has_board_been_setup(vboard, is_board_setup)
            if is_board_setup:
                cached_board = vboard
                print("Board has been setup")
            else:
                print("Setup the board")
                print_board(vboard)
       
        
        if is_board_setup:
            cached_board = make_move(vboard, cached_board, board)

        # print(board)

    else:
        print("Chessboard not found.")

    time.sleep(1)
