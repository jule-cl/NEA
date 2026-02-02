# main_window.py

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from screen_title import Title_Screen
from screen_creation import Creation_Screen
from screen_layout import Layout_Screen
from screen_clues import Clues_Screen
from screen_saved import Saved_Screen

from functools import partial

from app_settings import *

class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crossword Generator")
        self.setFixedSize(WINDOW_W, WINDOW_H)
        # self.setMinimumSize(800, 600)
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND};")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.current_screen = Title_Screen(lambda: self.goto_screen("create", []), lambda: self.goto_screen("saved"))
        self.stack.addWidget(self.current_screen)

    def goto_screen(self, screen, *data):
        self.__close_all_screens()
        match screen: 
            case "title":
                self.current_screen = Title_Screen(lambda: self.goto_screen("create"), lambda: self.goto_screen("saved"))
            case "create":
                self.current_screen = Creation_Screen(lambda: self.goto_screen("title"), partial(self.goto_screen, "layout"))
            case "layout":
                self.current_screen = Layout_Screen(data[0], lambda: self.goto_screen("title"), partial(self.goto_screen, "clues"))
            case "clues":
                self.current_screen = Clues_Screen(data[0], data[1], lambda: self.goto_screen("title"))
            case "saved":
                self.current_screen = Saved_Screen(lambda: self.goto_screen("title"))
            case _:
                raise ValueError(f"Unknown screen: {screen}")
            
        self.stack.addWidget(self.current_screen)
        self.stack.setCurrentWidget(self.current_screen)
        
    def __close_all_screens(self):
        for index in range(self.stack.count()):
            self.stack.removeWidget(self.stack.widget(index))
