# app_info.py

GRID_SIZES = [9, 11, 15]

# dimensions
WINDOW_W = 960 # 1536
WINDOW_H = 800 # 960
GRID_DIM = 500
WIDGET_PADDING = min(WINDOW_W, WINDOW_H)//60

EMPTY_CELL = ''
BLOCKED_CELL = '#'

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
    CELL_BASE = "#e5fff6"
