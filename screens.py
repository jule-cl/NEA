# pages.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt
from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller

class Title_Screen(QWidget):
    def __init__(self, go_to_grid_size):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

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
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Select Grid Size")
        label.setStyleSheet("font-size: 24px;")
        layout.addWidget(label)

        # Radio buttons for grid sizes
        self.size_buttons = QButtonGroup(self)
        for size in [5, 7, 9, 11, 13, 15]:
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
    def __init__(self, size, go_back):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel(f"Crossword Editor ({size}x{size})")
        layout.addWidget(title)

        # MVC setup
        model = CW_Model(size)
        view = CW_View(model)
        controller = CW_Controller(model, view)

        layout.addWidget(view)

        back_btn = QPushButton("Back to Menu")
        back_btn.clicked.connect(go_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)