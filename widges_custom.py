# button.py

from PyQt6.QtWidgets import QPushButton, QComboBox
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
        
class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(f"""
            QComboBox {{
                color: {Theme.BACKGROUND};
                background-color: {Theme.FOREGROUND};
                padding: 5px;
                border: 2px solid {Theme.FOREGROUND};
                border-radius: 6px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid {Theme.BACKGROUND};
            }}
            QComboBox::down-arrow {{
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {Theme.BACKGROUND};
            }}
            QComboBox QAbstractItemView {{
                color: {Theme.BACKGROUND};
                background-color: {Theme.FOREGROUND};
                selection-background-color: {Theme.BACKGROUND};
                selection-color: {Theme.FOREGROUND};
            }}
        """) 

        
