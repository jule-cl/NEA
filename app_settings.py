# app_info.py

# dimensions
WINDOW_W = 960 # 1536
WINDOW_H = 800 # 960
GRID_DIM = 500
WIDGET_PADDING = min(WINDOW_W, WINDOW_H)//60

EMPTY_CELL = ''
BLOCKED_CELL = '#'

# crossword visual related
BUFFER = 0.9
CELL_BORDER_WIDTH = 3
SELECTED_OUTLINE = 0.08
CLUE_NUMBER_BUFFER = 0.06
CLUE_NUMBER_SIZE = 0.4
CLUE_LETTER_SIZE = 0.7
TEXT_FONT = "Arial"

# generation related
GRID_SIZES = [9, 11, 15]
BASE_SELECTION_OPTIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "random"]

IMAGE_PATHS = ["images/pic_a.png", "images/pic_b.png", "images/pic_c.png"]

class CW_MODE:
    LAYOUT = "layout"
    CLUES = "clues"
    
class Theme:
    BACKGROUND = "#e5fff6"
    FOREGROUND = "#261b26"
    BLOCKED_CELL = "#261b26"
    SELECTED_CELL =  "#e9ff1f"
    SELECTED_WORD = "#f69221"
    HIGHLIGHT = "#173dff"
    CELL_BASE = "#eeeeee"
    
    BUTTON_ACTION = "#0f1317"
    BUTTON_DISABLED = "#cccccc"
    # BUTTON_HOVER = "#005a9e"
