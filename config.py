import cv2

# Calibration board parameters
CHESSBOARD_DIM = (6, 5)     # Number of corners (width, height)
CHESSBOARD_SIZE = 10e-3     # Side length of one square in meters (SI)

# Coil parameters
COILS_MAX_CURRENT = 5.
COILS_FPS = 5
COILS_NAME_OX = 'Dev/ao1'
COILS_NAME_OY = 'Dev/ao0'
COILS_NAME_IX = 'Dev/ai1'
COILS_NAME_IY = 'Dev/ai0'
COILS_MT_TO_V_X = 0.608
COILS_MT_TO_V_Y = 0.608

# Marker parameters
MARKER_SIZE = 5.08e-3       # Side length of marker in meters (SI)
MARKER_IS_INVERTED = True   # Is the marker black on white
MARKER_DICT = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)