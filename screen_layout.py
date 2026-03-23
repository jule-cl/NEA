# screen_layout.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

from widget_positioner import Widget_Positioner
from widgets_custom import Button, ComboBox
from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller
from app_info import *

class Layout_Screen(QWidget):
    """
    The screen for designing the crossword grid layout by toggling blocked cells.
    Displays the crossword grid alongside a panel with layout tools and statistics.

    Signals:
        mouse_clicked (QPointF): Emitted when the user clicks on the screen.
        key_pressed (int): Emitted when the user presses a key.

    Methods:
        mousePressEvent: Handles mouse click and emits mouse_clicked.
        keyPressEvent: Handles key press and emits key_pressed.
        get_symmetry: Returns the currently selected symmetry mode.
    """
    mouse_clicked = pyqtSignal(QPointF)
    key_pressed = pyqtSignal(int)
    
    def __init__(self, grid_size, crossword_title, back_to_title, go_to_clues):
        """
        Initialises the layout screen, setting up the MVC components and the GUI

        Args:
            grid_size (int): The size of the crossword grid to create.
            crossword_title (str): The title of the crossword being created.
            back_to_title (callable): Function to navigate back to the title screen.
            go_to_clues (callable): Function to navigate to the clues screen, passing the Crossword object as an argument.
        """
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # MVC setup
        self.cw_model = CW_Model(grid_size=grid_size, title=crossword_title) # model 
        self.cw_view = CW_View(self.cw_model) # view -> reference to model
        self.cw_view.setParent(self)
        self.cw_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cw_controller = CW_Controller(self.cw_model, self.cw_view, CW_MODE.LAYOUT, self) # controller -> reference to both
        self.mouse_clicked.connect(self.cw_controller.handle_mouse_clicked)
        self.key_pressed.connect(self.cw_controller.handle_key_pressed)
        
        # title
        title = QLabel("EDITING LAYOUT", self)
        title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 24px;")
        # info box
        self.info_box = Layout_Info_Box(self.cw_controller)
        self.info_box.setParent(self)
        self.cw_controller.update_info.connect(self.info_box.update)
        # leave
        leave_button = Button("Back to Menu", self)
        leave_button.clicked.connect(back_to_title)
        # next
        next_button = Button("Go next", self)
        next_button.clicked.connect(lambda: go_to_clues(self.cw_model.get_crossword_object()))
        
        self.cw_controller.draw() # puts crossword grid onto view
        self.show() # the elements don't have a width/height before they are on the screen, so show() first
        # move stuff
        Widget_Positioner.middle_left(self.cw_view, WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.top_center(title, WINDOW_W//2, WIDGET_PADDING)
        Widget_Positioner.middle_right(self.info_box, WINDOW_W-4*WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.bottom_left(leave_button, WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        Widget_Positioner.bottom_right(next_button, WINDOW_W-WIDGET_PADDING, WINDOW_H-WIDGET_PADDING)
        
    def mousePressEvent(self, event):
        """
        Handles a mouse click, converting the screen position to view coordinates and emitting the mouse_clicked signal.

        Args:
            event (QMouseEvent): The mouse press.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            screen_pos = event.position()
            view_pos = self.cw_view.mapFrom(self, screen_pos)
            self.mouse_clicked.emit(view_pos)
            
    def keyPressEvent(self, event):
        """
        Handles a key press event by emitting the key_pressed signal with the key.

        Args:
            event (QKeyEvent): The key press.
        """
        self.key_pressed.emit(event.key())
        
    def get_symmetry(self):
        """
        Returns the symmetry mode currently selected in the info box.

        Returns:
            int: The selected symmetry mode.
        """
        return self.info_box.get_symmetry()
        
class Layout_Info_Box(QWidget):
    """
    A panel displayed alongside the crossword grid on the layout screen.
    Contains layout generation tools and updating grid statistics.

    Methods:
        generate_layout: Calls layout generation using the current base and symmetry settings via the controller.
        get_symmetry: Returns the currently selected symmetry value.
        update: Refreshes all statistics labels and button states based on current grid state.
    """
    def __init__(self, cw_controller):
        """
        Initialises the info box with layout tools and statistics labels.

        Args:
            cw_controller (CW_Controller): The controller used to read and modify the grid.
        """
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
        # generate layout layout
        self.generate_layout_layout = QHBoxLayout()
        self.generate_layout_layout.setSpacing(10)
        # base pattern selection
        self.base_selection = ComboBox()
        self.base_selection.addItems(BASE_SELECTION_OPTIONS)
        self.base_selection.setCurrentIndex(3) # defaults to "bottom-right", as it is most common
        self.base_selection.currentIndexChanged.connect(self.update)
        # symmetry options
        self.symmetry_options = ComboBox()
        self.symmetry_options.addItems(SYMMETRY_OPTIONS.keys()) 
        self.symmetry_options.setCurrentIndex(1) # defaults to "2-fold", as it is most common  
        self.symmetry_options.currentIndexChanged.connect(self.update)
        # fill button (next to dropdown)
        self.fill_button = Button("Generate", self)
        self.fill_button.clicked.connect(self.generate_layout)
        self.generate_layout_layout.addWidget(self.base_selection)
        self.generate_layout_layout.addWidget(self.symmetry_options)
        self.generate_layout_layout.addWidget(self.fill_button)
        # empty button
        self.empty_button = Button("Empty grid", self)
        self.empty_button.clicked.connect(self.cw_controller.empty_grid)
        # errors button
        self.errors_button = Button("Check/Show errors", self)
        # put in overall layout
        actions_layout.addWidget(self.actions_title)
        actions_layout.addLayout(self.generate_layout_layout)
        actions_layout.addWidget(self.empty_button)
        actions_layout.addWidget(self.errors_button)
        overall_layout.addLayout(actions_layout)
        
        # section 2 (info)
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_container.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.SECONDARY_BACKGROUND};
                border-radius: 10px;
            }}
            QLabel#StatsTitle {{
                color: {Theme.FOREGROUND};
                font-size: 20px;
                font-weight: 600;
            }}
            QLabel#StatsLabel {{
                color: {Theme.FOREGROUND};
                font-size: 18px;
            }}
        """)

        # title
        stats_title = QLabel("Layout Statistics")
        stats_title.setObjectName("StatsTitle")
        # labels
        self.grid_size = QLabel()
        self.blocked_empty = QLabel()
        self.percentage_blocked = QLabel()
        self.longest_length = QLabel()
        self.common_length = QLabel()
        self.average_length = QLabel()
        self.no_of_words = QLabel()
        self.checked_cells = QLabel()
        all_labels = [
            self.grid_size, self.blocked_empty, self.percentage_blocked,
            self.longest_length, self.common_length, self.average_length,
            self.no_of_words, self.checked_cells
        ]

        # add to layout
        info_layout.addWidget(stats_title)
        info_layout.addSpacing(10)
        for label in all_labels:
            info_layout.addWidget(label)
            label.setObjectName("StatsLabel")
        overall_layout.addWidget(info_container)

        # initialise stats when screen loads
        self.update()
        
    def generate_layout(self):
        """
        Reads the current base pattern and symmetry selections and calls layout generation via the controller.
        """
        base_pattern = self.base_selection.currentText()
        if base_pattern == BASE_SELECTION_OPTIONS[4]:
            seed = None
        else: seed = BASE_SELECTION_OPTIONS.index(base_pattern)
        self.cw_controller.generate_layout(3.6, seed, self.get_symmetry())
        
    def get_symmetry(self):
        """
        Returns the symmetry mode based on the current symmetry dropdown selection.

        Returns:
            int: The selected symmetry mode.
        """
        return SYMMETRY_OPTIONS[self.symmetry_options.currentText()]
        
    def update(self):
        """
        Refreshes the statistics labels and enabled states of buttons based on the current grid content and UI selections.
        """
        crossword = self.cw_controller.model.get_crossword_object()
        size = crossword.get_grid_size()

        total = size * size
        blocked = crossword.get_blocked_cells_count()
        empty = total - blocked
        ratio = blocked / total if total > 0 else 0
        
        word_lengths = crossword.get_all_word_lengths()
        no_of_words = sum(word_lengths.values())
        average_word_length = sum([k*v for k, v in word_lengths.items()])/no_of_words
        most_common_occurences = max(word_lengths.values())
        most_common_lengths = ", ".join([str(k) for k, v in word_lengths.items() if v==most_common_occurences])
        no_of_checked = crossword.get_checked_cells_count()
        
        # symmetry contradictions
        contradicts = (self.base_selection.currentText() in ["top-right", "bottom-left"])
        contradicts &= (self.symmetry_options.currentText() == "4-fold")
        # update buttons
        self.fill_button.setEnabled(self.cw_controller.is_grid_empty() and not contradicts)
        self.empty_button.setEnabled(not self.cw_controller.is_grid_empty())

        # fill labels
        self.grid_size.setText(f"Grid size: {size} x {size}")
        self.blocked_empty.setText(f"# of blocked/empty cells: {blocked}/{empty}")
        self.percentage_blocked.setText(f"Blocked ratio: {ratio:.2%}")
        self.longest_length.setText(f"Length of longest word: {max(word_lengths.keys())} ({word_lengths[max(word_lengths.keys())]})")
        self.common_length.setText(f"Most common length(s): {most_common_lengths} ({most_common_occurences})")
        self.average_length.setText(f"Average word length: {average_word_length:.2f}")
        self.no_of_words.setText(f"# of words: {no_of_words}")
        self.checked_cells.setText(f"# of checked cells: {no_of_checked}")
