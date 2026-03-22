# main_window.py

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from screen_title import Title_Screen
from screen_creation import Creation_Screen
from screen_layout import Layout_Screen
from screen_clues import Clues_Screen
from screen_saved import Saved_Screen
from crossword import Crossword
from widgets_custom import WarningBox

from functools import partial

from app_info import *

class Screen_Handler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crossword Generator")
        self.setFixedSize(WINDOW_W, WINDOW_H)
        # self.setMinimumSize(800, 600)
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND};")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.goto_screen("title", "")

    def goto_screen(self, dest, source, *data):
        # check for warnings 
        match dest:
            case "title":
                if source == "clues": 
                    warning = WarningBox("Confirm leaving? Crossword will be saved.")
                    if warning.clickedButton() == warning.confirm_button:
                        pass # open the next page
                    elif warning.clickedButton() == warning.reject_button:
                        return  # do nothing
            case "clues":
                if source == "layout": 
                    warning = WarningBox("Are you sure you are happy with the layout? This cannot be changed.")
                    if warning.clickedButton() == warning.confirm_button:
                        pass # open the next page
                    elif warning.clickedButton() == warning.reject_button:
                        return  # do nothing
            case _:
                pass
        # close active screens
        self.__close_all_screens()
        # open next screen
        match dest: 
            case "title":
                self.current_screen = Title_Screen(lambda: self.goto_screen("create", dest), lambda: self.goto_screen("saved", dest))
                if source == "clues": Crossword.save(data[0])
            case "create":
                self.current_screen = Creation_Screen(lambda: self.goto_screen("title", dest), partial(self.goto_screen, "layout", dest))
            case "layout":
                # receiving (grid_size, title)
                self.current_screen = Layout_Screen(data[0], data[1], lambda: self.goto_screen("title", dest), partial(self.goto_screen, "clues", dest))
            case "clues":
                # receiving (grid object) -- can be from screen_saved (loading a crossword), or from screen_layout
                self.current_screen = Clues_Screen(data[0], partial(self.goto_screen, "title", dest))
            case "saved":
                self.current_screen = Saved_Screen(
                    lambda: self.goto_screen("title", dest),
                    lambda filepath: self.goto_screen("clues", dest, Crossword.load(filepath))
                )
            case _:
                pass
            
        self.stack.addWidget(self.current_screen)
        self.stack.setCurrentWidget(self.current_screen)
        
    def __close_all_screens(self):
        for index in range(self.stack.count()):
            self.stack.removeWidget(self.stack.widget(index))
