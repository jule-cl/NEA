# cw_model.py

from app_settings import *

class CW_Model:
    def __init__(self, grid_size):
        from cw_grid import Grid
        
        self.__grid_size = grid_size
        self.__grid = Grid(self.__grid_size)
        
        self.__symmetry = 2 # defaults to 2-fold
                
        self.__selected_cell = None
        self.__selected_direction = 'A' # A or D, defaults to A

    def change_selection(self, new_r, new_c):        
        # case if deselect everything (-1, -1)
        if new_r == new_c == -1: 
            self.__selected_cell = None
            self.__selected_direction = 'A'
        
        # check if clicked on the same cell as already selected, if can change direction then do so
        elif self.__selected_cell == (new_r, new_c):
            if self.__grid.is_cell_corner((new_r, new_c)): self.__flip_selected_direction()
        
        # if new selection is in the same word, keep the direction
        elif (new_r, new_c) in self.get_cells_in_selected_word():
            self.__selected_cell = (new_r, new_c)
        
        # if new selection is corner, keep same direction
        elif self.__grid.is_cell_corner((new_r, new_c)):
            self.__selected_cell = (new_r, new_c)
            
        # only one direction
        else: 
            self.__selected_cell = (new_r, new_c)
            if self.__grid.is_cell_in_word(self.__selected_cell, 'A'): 
                self.__selected_direction = 'A'
            elif self.__grid.is_cell_in_word(self.__selected_cell, 'D'): 
                self.__selected_direction = 'D'
            else: 
                self.__selected_direction = 'A'
                
    def __flip_selected_direction(self):
        if self.__selected_direction == 'A': 
            self.__selected_direction = 'D'
        elif self.__selected_direction == 'D':
            self.__selected_direction = 'A'

    def toggle_blocked(self, row, col):
        self.__grid.toggle_blocked(row, col, self.__symmetry)

    def get_selected_cell(self):
        return self.__selected_cell

    def get_cells_in_selected_word(self):
        if not self.__selected_cell: return []
        
        grid = self.__grid.get_grid()
        if self.__selected_direction == 'A':
            drow, dcol = 0, 1
        elif self.__selected_direction == 'D':
            drow, dcol = 1, 0
            
        all_cells = set()
        for direction in [1, -1]: # forwards / backwards
            test_row, test_col = self.__selected_cell
            while 0 <= test_row <= self.__grid_size-1 and 0 <= test_col <= self.__grid_size-1:
                if grid[test_row][test_col] == BLOCKED_CELL: break
                all_cells.add((test_row, test_col))
                test_row += drow*direction
                test_col += dcol*direction
                
        return all_cells

    def get_grid_size(self):
        return self.__grid_size
    
    def get_grid(self):
        return self.__grid.get_grid()
    
    def set_grid(self, grid):
        if len(grid) != self.__grid_size: raise Exception("something's wrong")
        self.__grid.set_grid(grid)
    
    def get_numbered_cells(self):
        return self.__grid.get_numbered_cells()
    
    def generate_layout(self, symmetry=2, ratio=3.6, seed=3):
        self.__grid.generate_layout(symmetry, ratio, seed)
        