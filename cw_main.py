# cw_main.py

import sys
from PyQt5.QtWidgets import QApplication
# from cw_model import CW_Model
# from cw_view import CW_View
from cw_controller import CW_Controller

if __name__ == '__main__':
    
    # model (backbone logic) has no references 
    # view has reference to model (to know the information to display)
    # controller (manages input/info passing) needs a reference to both
    
    app = QApplication(sys.argv)
    
    controller = CW_Controller()
    controller.show_window()
    
    sys.exit(app.exec())
    
    