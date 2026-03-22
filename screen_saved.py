# screen_saved.py

from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from widgets_custom import Button, WarningBox
import os, json
from app_info import *

class Saved_Screen(QWidget):
    def __init__(self, goto_title, load_crossword):
        super().__init__()
        self.load_crossword = load_crossword  # function that loads the editor

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(WIDGET_PADDING, WIDGET_PADDING, WIDGET_PADDING, WIDGET_PADDING)

        # title
        title = QLabel("Saved Crosswords")
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.FOREGROUND}")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(title)

        # scrollable card area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"border: 2px solid {Theme.FOREGROUND}; border-radius: 6px")
        
        self.__card_container = QWidget()
        self.__card_layout = QGridLayout(self.__card_container)
        self.__card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__card_layout.setHorizontalSpacing(20)
        self.__card_layout.setVerticalSpacing(20)
        self.__card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__card_layout.setSpacing(12)
        scroll_area.setWidget(self.__card_container)
        main_layout.addWidget(scroll_area)

        # back button
        back_button = Button("Back")
        back_button.clicked.connect(goto_title)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.refresh()

    def refresh(self):
        # clear existing cards
        for i in range(self.__card_layout.count()-1, -1, -1):
            self.__card_layout.itemAt(i).widget().deleteLater()

        # load crosswords and create the corresponding cards
        with open(SAVED_INDEX_PATH) as f:
            index = json.load(f)
        if not index:
            empty_message = QLabel("No saved crosswords yet.")
            empty_message.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.FOREGROUND};")
            self.__card_layout.addWidget(empty_message)
            return
        
        for i, crossword in enumerate(index):
            row = i // CARDS_PER_ROW
            col = i % CARDS_PER_ROW
            self.__card_layout.addWidget(self.__make_card(crossword), row, col)

    def __make_card(self, crossword):
        card = QFrame()
        card.setFixedWidth(int(WINDOW_W*0.92//CARDS_PER_ROW))
        card.setFixedHeight(int(card.width()*0.9))
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.CELL_BASE};
                border: 2px solid {Theme.FOREGROUND};
                border-radius: 10px;
                padding: 10px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # title
        title_label = QLabel(crossword["title"])
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.FOREGROUND};border: none")
        # metadata
        meta_label = QLabel(f"{crossword["grid_size"]}x{crossword["grid_size"]} grid\nCreated on: {crossword["created_date"]}")
        meta_label.setStyleSheet(f"font-size: 12px; color: {Theme.FOREGROUND}; border: none")
        # add to layout
        layout.addWidget(title_label)
        layout.addWidget(meta_label)
        layout.addStretch()

        # action buttons
        button_row = QHBoxLayout()
        # open crossword
        open_button = Button("Open")
        open_button.clicked.connect(lambda: self.load_crossword(crossword["filename"]))
        # delete crossword
        delete_button = Button("Delete")
        delete_button.clicked.connect(lambda: self.__delete(crossword["filename"]))
        # add to the row
        button_row.addWidget(open_button)
        button_row.addWidget(delete_button)
        layout.addLayout(button_row)

        return card

    def __delete(self, filename):
        warning = WarningBox("Are you sure you want to delete this crossword?")
        if warning.clickedButton() == warning.confirm_button:
            pass # delete it
        elif warning.clickedButton() == warning.reject_button:
            return  # do nothing

        filepath = os.path.join(SAVED_FOLDER, f"{filename}.json")
        if os.path.exists(filepath):
            os.remove(filepath)

        with open(SAVED_INDEX_PATH) as f:
            index = json.load(f)
        index = [crossword for crossword in index if crossword["filename"] != filename]
        with open(SAVED_INDEX_PATH, "w") as f:
            json.dump(index, f, indent=2)

        self.refresh()
