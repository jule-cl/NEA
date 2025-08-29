# cw_main.py

from cw_model import CW_Model
from cw_view import CW_View
from cw_controller import CW_Controller

if __name__ == '__main__':
    
    # model (backbone logic) has no references 
    # view has reference to model (to know the information to display)
    # controller (manages input/info passing) needs a reference to both
    
    model = CW_Model()
    view = CW_View(model)
    controller = CW_Controller(model, view)
    
    # model.grid.randomise_letters()
    # model.grid.randomise_blocked_cells()
    view.draw_screen()
    
    while controller.running:
        controller.process_input()
    
    
    