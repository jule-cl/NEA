# clickable_image.py

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class Clickable_Image(QLabel):
    clicked = pyqtSignal(int)
    
    def __init__(self, image_path, data):
        super().__init__()
        self.data = data
        self.is_selected = False
        
        # Load image
        pixmap = QPixmap(image_path)
        scaled = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled)
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.data)
    
    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()
    
    def update_style(self):
        if self.is_selected:
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
