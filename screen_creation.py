# screen_creation.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from clickable_image import Clickable_Image
from widget_positioner import Widget_Positioner
from widgets_custom import Button
from app_info import *

class Creation_Screen(QWidget):
    """
    The screen where the user selects a grid size and enters a title before creating a new crossword puzzle.

    Variables:
        image_paths (list[str]): File paths for the grid size preview images.
        selected_grid_size (int or None): The currently selected grid size, or None if none selected.
        title_text (str): The current contents of the title input field.
        grid_size_labels (dict[int, Clickable_Image]): Maps grid sizes to their image widgets.
        title_input (QLineEdit): The text input for the crossword title.
        continue_button (Button): The button to proceed to the layout screen, enabled only when both a grid size and title have been provided.

    Methods:
        deselect_all: Deselects all grid size images.
        on_image_clicked: Handles a grid size image being clicked.
    """
    def __init__(self, goto_title_screen, goto_layout_screen):
        """
        Initialises the creation screen with grid size selection images, a title input field, and navigation buttons.

        Args:
            goto_title_screen (callable): Function that sends user back to title screen
            goto_layout_screen (callable): Function that send user forward to layout screen, passing grid_size (int) and title (str) as arguments.
        """
        super().__init__()
        self.image_paths = IMAGE_PATHS
        self.selected_grid_size = None
        self.title_text = ""
        
        layout = QVBoxLayout()
        
        # screen title
        text = QLabel("Select Grid Size")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {Theme.FOREGROUND}")
        layout.addWidget(text)
        
        # images layout
        grid_size_labels_layout = QHBoxLayout()
        self.grid_size_labels = {}
        for i in range(len(GRID_SIZES)):
            image = IMAGE_PATHS[i]
            grid_size = GRID_SIZES[i]
            label = Clickable_Image(image, grid_size)
            label.clicked.connect(self.on_image_clicked)
            self.grid_size_labels[GRID_SIZES[i]] = label
            grid_size_labels_layout.addWidget(label)
        layout.addLayout(grid_size_labels_layout)
        
        # title text box
        title_label = QLabel("Enter Crossword Title:")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"font-size: 18px; margin-top: 20px; color: {Theme.FOREGROUND}")

        # enter title text field
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Crossword Title...")
        self.title_input.setMaxLength(40)
        self.title_input.textChanged.connect(self.__on_title_changed)
        self.title_input.setFixedWidth(300)
        self.title_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                font-size: 16px;
                border: 2px solid {Theme.FOREGROUND};
                border-radius: 6px;
                color: {Theme.FOREGROUND};
            }}
        """)
        layout.addWidget(title_label)
        layout.addWidget(self.title_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # continue button
        self.continue_button = Button("Continue")
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(lambda: goto_layout_screen(self.selected_grid_size, self.title_text))
        self.continue_button.setFixedWidth(200)
        
        layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        # back button
        back_button = Button("Back", self)
        back_button.clicked.connect(goto_title_screen)
        back_button.setFixedWidth(200)
        
        self.show()
        self.setLayout(layout)
        Widget_Positioner.bottom_left(back_button, WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
    
    def deselect_all(self):
        """
        Deselects all grid size image widgets.
        """
        for label in self.grid_size_labels.values():
            label.set_selected(False)
    
    def on_image_clicked(self, data):
        """
        Handles a grid size image being clicked, selecting it and updating the continue button state.

        Args:
            data (int): The grid size represented by the clicked image.
        """
        self.deselect_all()
        self.grid_size_labels[data].set_selected(True)
        self.selected_grid_size = data
        self.__update_continue_state()
        
    def __on_title_changed(self, text):
        """
        Handles changes to the title input field, updating the stored title text and the continue button state.

        Args:
            text (str): The current contents of the title input field.
        """
        self.title_text = text.strip()
        self.__update_continue_state()

    def __update_continue_state(self):
        """
        Enables the continue button only if both a grid size has been selected and a non-empty title has been entered.
        """
        self.continue_button.setEnabled((self.selected_grid_size is not None) and (len(self.title_text) > 0))
        