# widgets_custom.py

from PyQt6.QtWidgets import QPushButton, QComboBox, QMessageBox, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from app_info import *

class Button(QPushButton):
    """
    A custom widget inherited from QPushButton which styles it according to the theme.
    The cursor is also set to the pointing hand whenever the button is hovered.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialises the button with theme styling and a pointing hand cursor.
        """
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
    """
    A custom widget inherited from QComboBox which styles it according to the theme.
    """
    def __init__(self, *args, **kwargs):
        """Initialises the combobox with theme styling."""
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
    """
    A custom widget inherited from QMessageBox used to prompt the user to confirm or reject an action.

    Variables:
        confirm_button (QPushButton): The Yes button, with AcceptRole.
        reject_button (QPushButton): The No button, with RejectRole.
    """
    def __init__(self, text, comfirmation=True, *args, **kwargs):
        """
        Initialises and immediately displays the warning box with the given message.
        Each warning box will have two buttons: one for confirming and one for rejecting.
        The subsequent action perform will be determined by the button pressed.

        Args:
            text (str): The message to display in the warning box.
        """
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
        
        if comfirmation:
            self.confirm_button = self.addButton("Yes", QMessageBox.ButtonRole.AcceptRole)
            self.reject_button = self.addButton("No", QMessageBox.ButtonRole.RejectRole)
        else:
            self.continue_button = self.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        
        self.exec()

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
