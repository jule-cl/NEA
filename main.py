# cw_main.py

import sys
from PyQt6.QtWidgets import QApplication
from main_window import Main_Window

if __name__ == '__main__':

    app = QApplication(sys.argv)
    
    main_window = Main_Window()
    main_window.show()
    
    sys.exit(app.exec())
    