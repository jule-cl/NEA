# title_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from app_settings import *

class Title_Screen(QWidget):
    def __init__(self, go_to_grid_size):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Cryptic Crossword Builder")
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.FOREGROUND};")
        layout.addWidget(title)

        start_button = QPushButton("Create New Crossword")
        start_button.setFixedWidth(200)
        start_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND};")
        start_button.clicked.connect(go_to_grid_size)
        layout.addWidget(start_button)

        self.setLayout(layout)