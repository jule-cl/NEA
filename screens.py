# screens.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup, QGraphicsRectItem
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller
from app_settings import *

class Title_Screen(QWidget):
    def __init__(self, go_to_grid_size):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Cryptic Crossword Builder")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)

        start_btn = QPushButton("Create New Crossword")
        start_btn.setFixedWidth(200)
        start_btn.clicked.connect(go_to_grid_size)
        layout.addWidget(start_btn)

        self.setLayout(layout)
        
class Grid_Size_Screen(QWidget):
    def __init__(self, go_to_crossword):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Select Grid Size")
        label.setStyleSheet("font-size: 24px;")
        layout.addWidget(label)

        # Radio buttons for grid sizes
        self.size_buttons = QButtonGroup(self)
        for size in GRID_SIZES:
            btn = QRadioButton(f"{size} x {size}")
            layout.addWidget(btn)
            self.size_buttons.addButton(btn, size)
        layout.addSpacing(10)

        # Continue button
        confirm_btn = QPushButton("Continue")
        confirm_btn.clicked.connect(lambda: go_to_crossword(self.get_selected_size()))
        layout.addWidget(confirm_btn)

        self.setLayout(layout)

    def get_selected_size(self):
        checked = self.size_buttons.checkedId()
        return checked if checked != -1 else 9  # default 9x9
     
class Crossword_Screen(QWidget):
    mouse_clicked = pyqtSignal(QPointF)
    key_pressed = pyqtSignal(int)
    
    def __init__(self, size, go_back):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout = QVBoxLayout()

        title = QLabel(f"Crossword Editor ({size}x{size})")
        layout.addWidget(title)

        # MVC setup
        self.cw_model = CW_Model(size)
        self.cw_view = CW_View(self.cw_model)
        self.cw_controller = CW_Controller(self.cw_model, self.cw_view)
        self.cw_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.mouse_clicked.connect(self.cw_controller.handle_mouse_clicked)
        self.key_pressed.connect(self.cw_controller.handle_key_pressed)

        layout.addWidget(self.cw_view)

        back_btn = QPushButton("Back to Menu")
        back_btn.clicked.connect(go_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            screen_pos = event.position()
            view_pos = self.cw_view.mapFrom(self, screen_pos)
            
            self.mouse_clicked.emit(view_pos)
            
    def keyPressEvent(self, event):
        self.key_pressed.emit(event.key())
        