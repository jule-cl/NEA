# cw_model.py

class CW_Model:
    def __init__(self):
        from cw_grid import Grid
        
        self.grid = Grid(9)
        self.__listeners = []
        
    def register_listener(self, listener):
        self.__listeners.append(listener)
        
    def __notify(self, event):
        for listener in self.__listeners:
            listener(event)
            
    """
    GETTERS
    """
    def get_grid(self):
        return self.grid.get_grid()
    
    def get_grid_size(self):
        return self.grid.get_grid_size()
        
class Model_Event:
    def __init__(self, message):
        self.message = message    
    