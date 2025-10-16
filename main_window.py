from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from screens import *
from app_settings import *

class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crossword Generator")
        self.setFixedSize(WINDOW_W, WINDOW_H)
        # self.setMinimumSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create all pages
        self.title_screen = Title_Screen(self.show_grid_size_screen)
        self.grid_size_screen = Grid_Size_Screen(self.show_crossword_screen)

        # Add to stack
        self.stack.addWidget(self.title_screen)
        self.stack.addWidget(self.grid_size_screen)

    def show_grid_size_screen(self):
        self.stack.setCurrentWidget(self.grid_size_screen)

    def show_crossword_screen(self, size):
        self.crossword_screen = Crossword_Screen(size, self.close_crossword_screen)
        self.stack.addWidget(self.crossword_screen)
        self.stack.setCurrentWidget(self.crossword_screen)

    def close_crossword_screen(self):
        # back to title
        self.show_title_screen()
        
        # delete crossword screen from stack
        index = self.stack.indexOf(self.crossword_screen)
        try:
            widget = self.stack.widget(index)
            self.stack.removeWidget(widget)
            widget.deleteLater()
            self.crossword = None
        except IndexError:
            raise Exception("crossword screen doesn't exist")

    def show_title_screen(self):
        self.stack.setCurrentWidget(self.title_screen)
