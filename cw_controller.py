# cw_controller.py

from cw_view import CW_View
import threading

class CW_Controller:
    """Controller to coordinate between model and view"""
    def __init__(self):
        self.view = CW_View()
        # In a real crossword, you'd have a model for the puzzle data
        
    def show_window(self):
        self.view.show()