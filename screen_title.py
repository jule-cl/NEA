# title_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from app_settings import *

class Title_Screen(QWidget):
    def __init__(self, goto_creation):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Cryptic Crossword Builder")
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.FOREGROUND};")
        layout.addWidget(title)

        # create
        create_button = QPushButton("Create New Crossword")
        create_button.setFixedWidth(200)
        create_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND};")
        create_button.clicked.connect(goto_creation)
        layout.addWidget(create_button)
        
        # saved
        saved_button = QPushButton("Open Saved Crosswords")
        saved_button.setFixedWidth(220)
        saved_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND};")
        # saved_button.clicked.connect(goto_saved)
        layout.addWidget(saved_button)

        self.setLayout(layout)