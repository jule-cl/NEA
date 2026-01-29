# layout_screen.py

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox, QHBoxLayout
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
        self.cw_controller.update_info.connect(info_box.update_info)
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
        
        overall_layout = QVBoxLayout()
        overall_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        overall_layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(overall_layout)      
        
        # section 1 (actions)
        actions_layout = QVBoxLayout()
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        actions_layout.setSpacing(5)
        # title
        self.actions_title = QLabel("Layout Tools")
        self.actions_title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 18px; font-weight: bold;")
        # generat layout layout
        self.generate_layout_layout = QHBoxLayout()
        self.generate_layout_layout.setSpacing(10)
        # base pattern selection
        self.base_selection = QComboBox()
        self.base_selection.addItems(BASE_SELECTION_OPTIONS)
        self.base_selection.setStyleSheet(f"""
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
        # fill button (next to dropdown)
        self.fill_button = QPushButton("Generate", self)
        self.fill_button.clicked.connect(self.generate_layout)
        self.fill_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BUTTON_ACTION};
            }}
            QPushButton:disabled {{
                background-color: {Theme.BUTTON_DISABLED}
            }}
        """)
        self.generate_layout_layout.addWidget(self.base_selection)
        self.generate_layout_layout.addWidget(self.fill_button)
        # empty button (click to empty grid)
        self.empty_button = QPushButton("Empty grid", self)
        self.empty_button.clicked.connect(self.cw_controller.empty_grid)
        self.empty_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BUTTON_ACTION};
            }}
            QPushButton:disabled {{
                background-color: {Theme.BUTTON_DISABLED}
            }}
        """)
        # errors button
        self.errors_button = QPushButton("Check/Show errors", self)
        self.errors_button.setStyleSheet(f"background-color: {Theme.BUTTON_ACTION}")
        # put in overall layout
        actions_layout.addWidget(self.actions_title)
        actions_layout.addLayout(self.generate_layout_layout)
        actions_layout.addWidget(self.empty_button)
        actions_layout.addWidget(self.errors_button)
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
        
    def generate_layout(self):
        base_pattern = self.base_selection.currentText()
        if base_pattern == BASE_SELECTION_OPTIONS[4]:
            seed = None
        else: seed = BASE_SELECTION_OPTIONS.index(base_pattern)
        self.cw_controller.generate_layout(2, 3.6, 13, seed)
        
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
        
        # update buttons
        self.update_fillable_state()
        self.update_emptyable_state()
        
    def update_fillable_state(self):
        self.fill_button.setEnabled(self.cw_controller.is_grid_empty())
        
    def update_emptyable_state(self):
        self.empty_button.setEnabled(not self.cw_controller.is_grid_empty())
