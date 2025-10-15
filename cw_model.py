# cw_model.py

class CW_Model:
    def __init__(self, size):
        from cw_grid import Grid
        
        self.__grid_size = size
        self.__grid = Grid(size)

    def get_grid_size(self):
        return self.__grid_size
    
    def get_grid(self):
        return self.__grid.get_borderless_grid()