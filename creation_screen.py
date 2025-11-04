# creation_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from clickable_image import Clickable_Image
from app_settings import *

class Creation_Screen(QWidget):
    def __init__(self, goto_layout_screen):
        super().__init__()
        self.image_paths = IMAGE_PATHS
        self.selected_grid_size = None
        
        layout = QVBoxLayout()
        
        # text
        text = QLabel("Select Grid Size")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {Theme.FOREGROUND}")
        layout.addWidget(text)
        
        # labels_layout
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
        
        # continue button
        self.continue_button = QPushButton("Continue")
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(lambda: goto_layout_screen(self.selected_grid_size))
        self.continue_button.setFixedWidth(200)
        self.continue_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 16px;
                background-color: #0078d4;
                color: white;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        
        layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)
    
    def deselect_all(self):
        for label in self.grid_size_labels.values():
            label.set_selected(False)
    
    def on_image_clicked(self, data):
        self.deselect_all()
        self.grid_size_labels[data].set_selected(True)
        self.selected_grid_size = data
        self.continue_button.setEnabled(True)