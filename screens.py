# screens.py

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup, QGraphicsRectItem
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller
from clickable_image import Clickable_Image
from app_settings import *

class Widget_Positioner:
    @staticmethod
    def center(widget, x, y):
        widget.move(x - widget.width() // 2, y - widget.height() // 2)
    
    @staticmethod
    def top_left(widget, x, y):
        widget.move(x, y)
    
    @staticmethod
    def top_right(widget, x, y):
        widget.move(x - widget.width(), y)
    
    @staticmethod
    def top_center(widget, x, y):
        widget.move(x - widget.width() // 2, y)
    
    @staticmethod
    def bottom_left(widget, x, y):
        widget.move(x, y - widget.height())
    
    @staticmethod
    def bottom_right(widget, x, y):
        widget.move(x - widget.width(), y - widget.height())
    
    @staticmethod
    def bottom_center(widget, x, y):
        widget.move(x - widget.width() // 2, y - widget.height())
    
    @staticmethod
    def middle_left(widget, x, y):
        widget.move(x, y - widget.height() // 2)
    
    @staticmethod
    def middle_right(widget, x, y):
        widget.move(x - widget.width(), y - widget.height() // 2)

class Title_Screen(QWidget):
    def __init__(self, go_to_grid_size):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Cryptic Crossword Builder")
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.FOREGROUND};")
        layout.addWidget(title)

        start_button = QPushButton("Create New Crossword")
        start_button.setFixedWidth(200)
        start_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND};")
        start_button.clicked.connect(go_to_grid_size)
        layout.addWidget(start_button)

        self.setLayout(layout)
        
class Grid_Size_Screen(QWidget):
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
     
class Layout_Screen(QWidget):
    mouse_clicked = pyqtSignal(QPointF)
    key_pressed = pyqtSignal(int)
    
    def __init__(self, size, back_to_title, go_next):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # MVC setup
        self.cw_model = CW_Model(size) # model 
        self.cw_view = CW_View(self.cw_model) # view -> reference to model
        self.cw_view.setParent(self)
        self.cw_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cw_controller = CW_Controller(self.cw_model, self.cw_view, CW_MODE.LAYOUT) # controller -> reference to both
        self.mouse_clicked.connect(self.cw_controller.handle_mouse_clicked)
        self.key_pressed.connect(self.cw_controller.handle_key_pressed)
        
        # title
        title = QLabel("EDITING LAYOUT", self)
        title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 24px;")
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
        Widget_Positioner.bottom_left(leave_button, WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        Widget_Positioner.bottom_right(next_button, WINDOW_W-WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            screen_pos = event.position()
            view_pos = self.cw_view.mapFrom(self, screen_pos)
            
            self.mouse_clicked.emit(view_pos)
            
    def keyPressEvent(self, event):
        self.key_pressed.emit(event.key())

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
        # leave
        leave_button = QPushButton("Back to Menu", self)
        leave_button.setStyleSheet(f"background-color: {Theme.FOREGROUND}; color: {Theme.BACKGROUND}")
        leave_button.clicked.connect(go_back)

        self.cw_controller.draw()
        self.show()
        # move stuff
        Widget_Positioner.middle_left(self.cw_view, WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.top_center(title, WINDOW_W//2, WIDGET_PADDING)
        Widget_Positioner.bottom_left(leave_button, WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            screen_pos = event.position()
            view_pos = self.cw_view.mapFrom(self, screen_pos)
            
            self.mouse_clicked.emit(view_pos)
            
    def keyPressEvent(self, event):
        self.key_pressed.emit(event.key())

