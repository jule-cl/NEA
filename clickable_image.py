# clickable_image.py

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class Clickable_Image(QLabel):
    """
    Custom widget that displays an image, and can be selected.
    
    Parent class: QLabel
    
    Variables:
        grid_size (int): Stores the grid size that the image represents.
        __is_selected (bool): Keeps track of whether the image is selected.
        clicked: A class variable which emits a signal along with the grid_size when the image has been clicked.
    
    Methods:
        update_style: Updates the style sheet of this widget depending on whether the image is selected or not.

    Setters:
        set_selected: Sets the __is_selected variable. Updates the styling afterwards as well.
    """
    clicked = pyqtSignal(int)
    
    def __init__(self, image_path, grid_size, *args, **kwargs):
        """
        Initialises the clickable image class.
        
        Args:
            image_path (str): The file path of image to be displayed by the label.
            grid_size (int): The grid size that this image should represent, and the one that will be selected when chosen.
        """
        super().__init__(*args, **kwargs)
        self.grid_size = grid_size
        self.__is_selected = False
        
        # Load image
        pixmap = QPixmap(image_path)
        scaled = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled)
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()
    
    def mousePressEvent(self, event):
        """Detects when this label has been clicked, and emits the class variable clicked along with the grid size chosen"""
        self.clicked.emit(self.grid_size)
    
    def set_selected(self, selected):
        """
        Sets the selected state of this image, and updates the styling afterwards.
        
        Args:
            selected (bool): The state that the image should be set to.
        """
        self.__is_selected = selected
        self.update_style()
    
    def update_style(self):
        """Updates the style sheet depending on whether the image is selected or not."""
        if self.__is_selected:
            self.setStyleSheet("""
                QLabel {
                    border: 5px solid #0078d4;
                    border-radius: 10px;
                    padding: 5px;
                    background-color: #e6f2ff;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 3px solid #ccc;
                    border-radius: 10px;
                    padding: 5px;
                }
                QLabel:hover {
                    border: 3px solid #999;
                }
            """)
