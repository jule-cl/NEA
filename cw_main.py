# cw_main.py

import cw_model
import cw_view
import cw_controller

if __name__ == '__main__':
    
    # model (backbone logic) has no references 
    # view has reference to model (to know the information to display)
    # controller (manages input/info passing) needs a reference to both
    
    model = cw_model.CW_Model()
    view = cw_view.CW_View(model)
    controller = cw_controller.CW_Controller(model, view)
    
    # model.grid.randomise_letters()
    # model.grid.randomise_blocked_cells()
    # view.draw_screen()
    
    while controller.running:
        view.window.mainloop()
    
    
    