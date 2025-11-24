# clues_screen.py

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

from widget_positioner import Widget_Positioner
from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller
from app_settings import *

class Clues_Screen(QWidget):
    mouse_clicked = pyqtSignal(QPointF)
    key_pressed = pyqtSignal(int)
    
    def __init__(self, grid_size, grid, go_back):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # MVC setup
        self.cw_model = CW_Model(grid_size)
        self.cw_model.set_grid(grid)
        self.cw_view = CW_View(self.cw_model)
        self.cw_view.setParent(self)
        self.cw_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cw_controller = CW_Controller(self.cw_model, self.cw_view, CW_MODE.CLUES)
        self.mouse_clicked.connect(self.cw_controller.handle_mouse_clicked)
        self.key_pressed.connect(self.cw_controller.handle_key_pressed)
        
        # title
        title = QLabel("EDITING CLUES", self)
        title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 24px")
        # info box
        info_box = Clues_Info_Box(self.cw_controller)
        info_box.setParent(self)
        self.cw_controller.update_info.connect(info_box.update_info)
        # leave
        leave_button = QPushButton("Back to Menu", self)
        leave_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        leave_button.clicked.connect(go_back)

        self.cw_controller.draw()
        self.show()
        # move stuff
        Widget_Positioner.middle_left(self.cw_view, WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.top_center(title, WINDOW_W//2, WIDGET_PADDING)
        Widget_Positioner.middle_right(info_box, WINDOW_W-WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.bottom_left(leave_button, WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            screen_pos = event.position()
            view_pos = self.cw_view.mapFrom(self, screen_pos)
            
            self.mouse_clicked.emit(view_pos)
            
    def keyPressEvent(self, event):
        self.key_pressed.emit(event.key())
        
class Clues_Info_Box(QWidget):
    def __init__(self, cw_controller):
        super().__init__()
        self.cw_controller = cw_controller
        
        self.setFixedWidth(int(WINDOW_W*0.35))
        self.setFixedHeight(int(WINDOW_H*0.8))
        
        overall_layout = QVBoxLayout()
        overall_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        overall_layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(overall_layout)      
        
        # section 1 (actions)
        actions_layout = QVBoxLayout()
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # title
        self.actions_title = QLabel("Clues Tools")
        self.actions_title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 18px; font-weight: bold;")
        # fill button (click to autofill)
        self.autofill_button = QPushButton("Autofill", self)
        self.autofill_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        self.autofill_button.setFixedWidth(120)
        self.autofill_button.clicked.connect(lambda: self.cw_controller.autofill(constraint=5))
        # empty button (click to empty grid)
        self.clear_button = QPushButton("Clear words", self)
        self.clear_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        self.clear_button.setFixedWidth(100)
        self.clear_button.clicked.connect(self.cw_controller.clear_grid)
        # put in overall layout
        actions_layout.addWidget(self.actions_title)
        actions_layout.addWidget(self.autofill_button)
        actions_layout.addWidget(self.clear_button)
        overall_layout.addLayout(actions_layout)
        
        # section 2 (info)
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # title
        stats_title = QLabel("Layout Statistics")
        stats_title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 18px; font-weight: bold;")
        # labels
        self.stat_block_ratio = QLabel()
        self.stat_block_count = QLabel()
        self.stat_open_count = QLabel()
        self.stat_grid_size = QLabel()
        for lbl in [
            self.stat_block_ratio,
            self.stat_block_count,
            self.stat_open_count,
            self.stat_grid_size
        ]:
            lbl.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 14px;")
        # put in overall layout
        info_layout.addWidget(stats_title)
        info_layout.addSpacing(5)
        info_layout.addWidget(self.stat_block_ratio)
        info_layout.addWidget(self.stat_block_count)
        info_layout.addWidget(self.stat_open_count)
        info_layout.addWidget(self.stat_grid_size)
        overall_layout.addLayout(info_layout)

        # initialize stats when screen loads
        self.update_info()
        
    def update_info(self):
        grid = self.cw_controller.model.get_grid()
        size = len(grid)

        total = size * size
        blocked = sum(cell == "#" for row in grid for cell in row)
        open_cells = total - blocked

        ratio = blocked / total if total > 0 else 0

        # fill labels
        self.stat_grid_size.setText(f"Grid size: {size} * {size}")
        self.stat_block_count.setText(f"Blocked cells: {blocked}")
        self.stat_open_count.setText(f"Open cells: {open_cells}")
        self.stat_block_ratio.setText(f"Blocked ratio: {ratio:.2%}")
