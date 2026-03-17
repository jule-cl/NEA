# clues_screen.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget, QScrollArea, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

from widget_positioner import Widget_Positioner
from widges_custom import Button, ComboBox
from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller
from app_settings import *

from word_funcs import Word_Funcs

class Clues_Screen(QWidget):
    mouse_clicked = pyqtSignal(QPointF)
    key_pressed = pyqtSignal(int)
    
    def __init__(self, grid, back_to_menu):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # MVC setup
        self.cw_model = CW_Model(crossword_object=grid)
        self.cw_view = CW_View(self.cw_model)
        self.cw_view.setParent(self)
        self.cw_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cw_controller = CW_Controller(self.cw_model, self.cw_view, CW_MODE.CLUES, self)
        self.mouse_clicked.connect(self.cw_controller.handle_mouse_clicked)
        self.key_pressed.connect(self.cw_controller.handle_key_pressed)
        
        # title
        title = QLabel("EDITING CLUES", self)
        title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 24px")
        # info box
        info_box = Clues_Info_Box(self.cw_controller)
        info_box.setParent(self)
        self.cw_controller.update_info.connect(info_box.update)
        # leave
        leave_button = Button("Save and back to Menu", self)
        leave_button.clicked.connect(lambda: back_to_menu(self.cw_model.get_crossword_object()))

        self.cw_controller.draw()
        self.show()
        # move stuff
        Widget_Positioner.middle_left(self.cw_view, WIDGET_PADDING, WINDOW_H//2)
        Widget_Positioner.top_center(title, WINDOW_W//2, WIDGET_PADDING)
        Widget_Positioner.middle_right(info_box, WINDOW_W-4*WIDGET_PADDING, WINDOW_H//2)
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

        self.setFixedWidth(int(WINDOW_W * 0.35))
        self.setFixedHeight(int(WINDOW_H * 0.8))

        overall_layout = QVBoxLayout()
        overall_layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(overall_layout)

        # Create tab widget
        self.tabs = QTabWidget()
        overall_layout.addWidget(self.tabs)

        # Create tabs
        self.actions_tab = self.create_actions_tab()
        self.clue_tab = self.create_clue_tab()
        self.stats_tab = self.create_stats_tab()

        # Add tabs
        self.tabs.addTab(self.actions_tab, "Actions")
        self.tabs.addTab(self.clue_tab, "Clue")
        self.tabs.addTab(self.stats_tab, "Statistics")

        self.tabs.setStyleSheet(f"""
        QTabWidget::pane {{
            border: 2px solid {Theme.FOREGROUND};
            background-color: red;
        }}

        QTabBar::tab {{
            background: {Theme.CELL_BASE};
            color: {Theme.FOREGROUND};
            padding: 8px 18px;
            border: 1px solid {Theme.FOREGROUND};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}

        QTabBar::tab:selected {{
            background: {Theme.SECONDARY_BACKGROUND};
            color: white;
            font-weight: bold;
        }}

        QTabBar::tab:hover {{
            background: {Theme.SELECTED_CELL};
        }}

        QTabBar::tab:!selected {{
            margin-top: 3px;
        }}
        """)

        self.update()
        
    def update(self):
        # actions tab
        self.autofill_button.setEnabled(self.cw_controller.is_grid_clear())
        self.clear_button.setEnabled(not self.cw_controller.is_grid_clear())
        selected_clue = self.cw_controller.get_selected_clue()
        # current clue and word
        word = "Selected word: "
        clue = "Selected clue: "
        if not selected_clue:
            clue += "N/A"
            word += "N/A"
        else:
            clue += f"{selected_clue.clue_number} {DIRECTION[selected_clue.direction]}"
            word += f"{Word_Funcs.displayed_to_word(selected_clue.word)} ({selected_clue.clue_length})"
        self.__current_clue_label.setText(clue)
        self.__current_word_label.setText(word)
        
        # clue tab
        for i, clue in enumerate(self.cw_controller.get_all_clues()):
            offset = int(clue.direction == 'D')+1
            self.__clue_grid.itemAtPosition(i+offset, 1).widget().setText(Word_Funcs.displayed_to_word(clue.word))
            clue.clue_sentence = self.__clue_grid.itemAtPosition(i+offset, 2).widget().text()

    def create_actions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(12)
        tab.setLayout(layout)

        title = QLabel("Clue Tools")
        title.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # autofill row: button + constraint combobox
        autofill_row = QHBoxLayout()
        self.autofill_button = Button("Autofill")
        self.autofill_button.clicked.connect(lambda: self.cw_controller.autofill(constraint=self.constraint_options.currentData()))
        self.constraint_options = ComboBox()
        for label, value in CONSTRAINT_OPTIONS:
            self.constraint_options.addItem(label, value)
        self.constraint_options.setCurrentIndex(1)  # default to 5
        autofill_row.addWidget(self.autofill_button)
        autofill_row.addWidget(self.constraint_options)
        layout.addLayout(autofill_row)

        # clear button below
        self.clear_button = Button("Clear all words")
        self.clear_button.clicked.connect(self.cw_controller.clear_grid)
        layout.addWidget(self.clear_button)

        # selected clue + word labels
        self.__current_clue_label = QLabel("")
        self.__current_word_label = QLabel("")
        for label in [self.__current_clue_label, self.__current_word_label]:
            label.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 18px;")
            layout.addWidget(label)

        return tab

    def create_clue_tab(self):
        tab = QWidget()
        outer_layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        container.setStyleSheet(f"""
            QLabel {{
                border: 1px solid {Theme.FOREGROUND};
                padding: 4px;
            }}
            QLineEdit {{
                border: 1px solid {Theme.FOREGROUND};
                padding: 4px;
            }}
        """)
        self.__clue_grid = QGridLayout(container)
        self.__clue_grid.setSpacing(0)
        self.__clue_grid.setContentsMargins(0, 0, 0, 0)

        # put each clue as a row
        # across header
        header = QLabel("Across")
        header.setStyleSheet(f"color: {Theme.FOREGROUND}; font-weight: bold; font-size: 13px;")
        self.__clue_grid.addWidget(header, 0, 0, 1, 3)
        down_section = False
        for i, clue in enumerate(self.cw_controller.get_all_clues()):
            clue_number = QLabel(f"{clue.clue_number}")
            clue_number.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 13px;")

            word_at_clue = QLabel(Word_Funcs.displayed_to_word(clue.word))
            word_at_clue.setStyleSheet(f"color: {Theme.FOREGROUND}; font-size: 13px;")

            sentence_input = QLineEdit()
            sentence_input.setPlaceholderText("_"*10)
            if clue.clue_sentence:
                sentence_input.setText(clue.clue_sentence)
            sentence_input.setStyleSheet(f"color: {Theme.FOREGROUND}")
            sentence_input.textChanged.connect(self.update)

            if clue.direction == 'D' and not down_section: 
                down_section = True
                header = QLabel("Down")
                header.setStyleSheet(f"color: {Theme.FOREGROUND}; font-weight: bold; font-size: 13px;")
                self.__clue_grid.addWidget(header, i+1, 0, 1, 3)
                
            self.__clue_grid.addWidget(clue_number, i+1+int(down_section), 0)
            self.__clue_grid.addWidget(word_at_clue, i+1+int(down_section), 1)
            self.__clue_grid.addWidget(sentence_input, i+1+int(down_section), 2)

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)
        return tab
        
    def create_stats_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        tab.setLayout(layout)

        self.stats_label = QLabel("Statistics will go here")
        self.stats_label.setStyleSheet(
            f"color: {Theme.FOREGROUND}; font-size: 14px;"
        )

        layout.addWidget(self.stats_label)

        return tab
