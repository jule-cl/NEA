# button.py

from PyQt6.QtWidgets import QPushButton, QComboBox, QMessageBox
from PyQt6.QtCore import Qt
from app_info import *

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

class WarningBox(QMessageBox):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText(text)
        self.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                color: {Theme.FOREGROUND};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {Theme.BUTTON_ACTION};
                color: {Theme.BACKGROUND};
                border-radius: 6px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BUTTON_HOVER};
            }}
        """)
        
        self.confirm_button = self.addButton("Yes", QMessageBox.ButtonRole.AcceptRole)
        self.reject_button = self.addButton("No", QMessageBox.ButtonRole.RejectRole)
        
        self.exec()
