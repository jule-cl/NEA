# screen_title.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from widgets_custom import Button
from app_info import *

class Title_Screen(QWidget):
    """
    The main title screen of the application, presenting the app name and navigation buttons to create a new crossword or open saved ones.
    """
    def __init__(self, goto_creation, goto_saved):
        """
        Initialises the title screen with a title label and navigation buttons.

        Args:
            goto_creation (callable): Function to navigate to the creation screen.
            goto_saved (callable): Function to navigate to the saved screen.
        """
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Cryptic Crossword Builder")
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.FOREGROUND};")
        layout.addWidget(title)
        layout.setSpacing(4)

        # create
        create_button = Button("Create New Crossword")
        create_button.setFixedWidth(200)
        create_button.clicked.connect(goto_creation)
        layout.addWidget(create_button)
        
        # saved
        saved_button = Button("Open Saved Crosswords")
        saved_button.setFixedWidth(220)
        saved_button.clicked.connect(goto_saved)
        layout.addWidget(saved_button)

        self.setLayout(layout)
