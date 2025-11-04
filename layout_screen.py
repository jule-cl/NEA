# layout_screen.py

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

from widget_positioner import Widget_Positioner
from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller
from app_settings import *

class Layout_Screen(QWidget):
    mouse_clicked = pyqtSignal(QPointF)
    key_pressed = pyqtSignal(int)
    
    def __init__(self, grid_size, back_to_title, go_next):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # MVC setup
        self.cw_model = CW_Model(grid_size) # model 
        self.cw_view = CW_View(self.cw_model) # view -> reference to model
        self.cw_view.setParent(self)
        self.cw_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cw_controller = CW_Controller(self.cw_model, self.cw_view, CW_MODE.LAYOUT) # controller -> reference to both
        self.mouse_clicked.connect(self.cw_controller.handle_mouse_clicked)
        self.key_pressed.connect(self.cw_controller.handle_key_pressed)
        
        # title
        title = QLabel("EDITING LAYOUT", self)
        title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 24px;")
        # info box
        info_box = Layout_Info_Box(self.cw_controller)
        info_box.setParent(self)
        # leave
        leave_button = QPushButton("Back to Menu", self)
        leave_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        leave_button.clicked.connect(back_to_title)
        # next
        next_button = QPushButton("Go next", self)
        next_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        next_button.clicked.connect(lambda: go_next(self.cw_model.get_grid_size(), self.cw_model.get_grid()))
        
        self.cw_controller.draw() # puts crossword grid onto view
        self.show() # the elements don't have a width/height before they are on the screen, so show() first
        # move stuff
        Widget_Positioner.middle_left(self.cw_view, WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.top_center(title, WINDOW_W//2, WIDGET_PADDING)
        Widget_Positioner.middle_right(info_box, WINDOW_W-WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.bottom_left(leave_button, WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        Widget_Positioner.bottom_right(next_button, WINDOW_W-WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            screen_pos = event.position()
            view_pos = self.cw_view.mapFrom(self, screen_pos)
            
            self.mouse_clicked.emit(view_pos)
            
    def keyPressEvent(self, event):
        self.key_pressed.emit(event.key())
        
class Layout_Info_Box(QWidget):
    def __init__(self, cw_controller):
        super().__init__()
        self.cw_controller = cw_controller
        
        self.setFixedWidth(int(WINDOW_W*0.35))
        self.setFixedHeight(int(WINDOW_H*0.8))
        
        info_box_layout = QVBoxLayout()
        info_box_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # fill button (click to generate a layout)
        self.fill_button = QPushButton("Generate layout", self)
        self.fill_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        self.fill_button.setFixedWidth(120)
        self.fill_button.clicked.connect(self.cw_controller.generate_layout)
        # empty button (click to empty grid)
        self.empty_button = QPushButton("Empty grid", self)
        self.empty_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        self.empty_button.setFixedWidth(100)
        self.empty_button.clicked.connect(self.cw_controller.empty_grid)
        # errors button
        self.errors_button = QPushButton("Check/Show errors", self)
        self.errors_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        self.errors_button.setFixedWidth(150)
        
        info_box_layout.addWidget(self.fill_button)
        info_box_layout.addWidget(self.empty_button)
        info_box_layout.addWidget(self.errors_button)
        self.setLayout(info_box_layout)
        
