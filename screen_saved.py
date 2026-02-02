# screen_saved.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from widget_positioner import Widget_Positioner
from app_settings import *

class Saved_Screen(QWidget):
    def __init__(self, goto_title):
        super().__init__()

        title = QLabel("Saved Crosswords", self)
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.FOREGROUND};")
        
        back_button = QPushButton("Back", self)
        back_button.setStyleSheet(f"background-color: {Theme.BUTTON_ACTION};")
        back_button.clicked.connect(goto_title)

        self.show()
        Widget_Positioner.top_center(title, WINDOW_W//2, WIDGET_PADDING)
        Widget_Positioner.bottom_left(back_button, WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        
        
