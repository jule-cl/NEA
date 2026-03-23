# app_info.py

"""
This file contains the constants which will be used throughout the program
"""

# dimensions
WINDOW_W = 1200 # 1536
WINDOW_H = 800 # 960
GRID_DIM = 500
WIDGET_PADDING = min(WINDOW_W, WINDOW_H)//60

EMPTY_CELL = '_'
BLOCKED_CELL = '#'

# crossword visual related
BUFFER = 0.9
CELL_BORDER_WIDTH = 3
SELECTED_OUTLINE = 0.08
CLUE_NUMBER_BUFFER = 0.06
CLUE_NUMBER_SIZE = 0.3
CLUE_LETTER_SIZE = 0.65
TEXT_FONT = "Arial"

# generation related
GRID_SIZES = [11, 13, 15]
BASE_SELECTION_OPTIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "random"]
SYMMETRY_OPTIONS = {"None":1, "2-fold":2, "4-fold":4}
DIRECTION = {'A': 'across', 'D':'down'}
CONSTRAINT_OPTIONS = [("Low", 3), ("Medium", 5), ("High", 8)]
WORD_DATA_FILE = "word_data.json"
IMAGE_PATHS = ["images/pic_a.png", "images/pic_b.png", "images/pic_c.png"]

# weights for scoring
class Weights:
    """
    A higher weight means more important
    The actual values that are lower are prioritised
    """
    WEIGHT_1 = 0.8 # most common word
    WEIGHT_2 = 0.2 # second common word
    WEIGHT_BASE = 1.5 # popularity of word
    WEIGHT_A = 2 # length of word
    WEIGHT_B = 0.05 # non-character words
    WEIGHT_C = 0 # letter frequency

# saving crosswords
SAVED_FOLDER = "saved_crosswords"
SAVED_INDEX_PATH = "saved_crosswords/index.json"
CARDS_PER_ROW = 3

class CW_MODE:
    LAYOUT = "layout"
    CLUES = "clues"
    
"""
Class that defines colour which will be used throughout the program
"""
class Theme:
    BACKGROUND = "#e5fff6"
    SECONDARY_BACKGROUND = "#c4c7c6"
    FOREGROUND = "#261b26"
    BLOCKED_CELL = "#261b26"
    SELECTED_CELL =  "#f4f76a"
    SELECTED_WORD = "#f69221"
    HIGHLIGHT = "#173dff"
    CELL_BASE = "#f4f7f6"
    
    BUTTON_ACTION = "#261b26"
    BUTTON_DISABLED = "#cccccc"
    BUTTON_HOVER = "#333333"
