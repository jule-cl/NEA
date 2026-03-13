# button.py

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from app_settings import *

class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px;
                background-color: {Theme.FOREGROUND};
                color: {Theme.BACKGROUND};
                border: none;
                border-radius: 5px;
                padding: 6px 8px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BUTTON_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {Theme.BUTTON_DISABLED};
                color: {Theme.FOREGROUND}
            }}""")
