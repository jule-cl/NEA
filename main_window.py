# main_window.py

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from screen_title import Title_Screen
from screen_creation import Creation_Screen
from screen_layout import Layout_Screen
from screen_clues import Clues_Screen

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

        # Create all pages
        self.title_screen = Title_Screen(self.goto_creation_screen)
        self.creation_screen = Creation_Screen(self.goto_layout_screen)

        # Add to stack
        self.stack.addWidget(self.title_screen)
        self.stack.addWidget(self.creation_screen)

    def goto_creation_screen(self):
        self.stack.setCurrentWidget(self.creation_screen)
        self.creation_screen.deselect_all()

    def goto_layout_screen(self, size):
        self.layout_screen = Layout_Screen(size, lambda: self.back_to_title("layout"), self.goto_clues_screen)
        self.stack.addWidget(self.layout_screen)
        self.stack.setCurrentWidget(self.layout_screen)
        
    def goto_clues_screen(self, grid_size, grid):
        self.__close_layout_screen()
        self.clues_screen = Clues_Screen(grid_size, grid, lambda: self.back_to_title("clues"))
        self.stack.addWidget(self.clues_screen)
        self.stack.setCurrentWidget(self.clues_screen)

    def back_to_title(self, current_page):
        self.show_title_screen()
        if current_page == "layout":
            self.__close_layout_screen()
        if current_page == "clues":
            self.__close_clues_screen()
        
    def __close_layout_screen(self):
        index = self.stack.indexOf(self.layout_screen)
        try:
            widget = self.stack.widget(index)
            self.stack.removeWidget(widget)
            widget.deleteLater()
            self.crossword = None
        finally:
            pass
            
    def __close_clues_screen(self):
        index = self.stack.indexOf(self.clues_screen)
        try:
            widget = self.stack.widget(index)
            self.stack.removeWidget(widget)
            widget.deleteLater()
            self.crossword = None
        finally:
            pass
        
    def show_title_screen(self):
        self.stack.setCurrentWidget(self.title_screen)
