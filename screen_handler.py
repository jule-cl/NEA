# screen_handler.py

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
    """
    The main application window, managing screen navigation using a QStackedWidget.
    Handles transitions between all screens, including warning dialogs before certain navigations.
    Triggers crossword saving when leaving the clues screen.

    Methods:
        goto_screen: Navigates to the specified screen, ocassionally showing a warning first depending the source and destination.
    """
    def __init__(self):
        """
        Initialises the main window, sets up the stacked widget.
        Starts by navigating to the title screen.
        """
        super().__init__()
        self.setWindowTitle("Crossword Generator")
        self.setFixedSize(WINDOW_W, WINDOW_H)
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND};")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.goto_screen("title", "")

    def goto_screen(self, dest, source, *data):
        """
        Depending on which screen the user is navigating to and from, display a warning message first.
        If the user confirms, delete all screens and create a new screen displaying the destination screen.
        The screen identifiers are only used in this method and are from the following:
            "title", "create", "layout", "clues", "saved"

        Args:
            dest (str): The destination screen identifier, where the user is navigating to.
            source (str): The source screen identifier, where the user is navigating from.
            *data: Additional data passed to the destination screen.
        """
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
        """
        Deletes all screens from the widget stack, closing them.
        """
        for index in range(self.stack.count()):
            self.stack.removeWidget(self.stack.widget(index))
