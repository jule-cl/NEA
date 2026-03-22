# cw_main.py

import sys
from PyQt6.QtWidgets import QApplication
from screen_handler import Screen_Handler
from app_info import *

if __name__ == '__main__':
    """
    Creates the main window which the application will be displayed on
    """
    app = QApplication(sys.argv)
            
    main_window = Screen_Handler()
    main_window.show()
    
    sys.exit(app.exec()) # closes the window properly
    