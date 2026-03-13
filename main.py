# cw_main.py

import sys
from PyQt6.QtWidgets import QApplication
from screen_handler import Screen_Handler
from app_settings import *

if __name__ == '__main__':

    app = QApplication(sys.argv)
            
    main_window = Screen_Handler()
    main_window.show()
    
    sys.exit(app.exec())
    