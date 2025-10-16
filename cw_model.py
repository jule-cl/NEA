# cw_model.py

from app_settings import *

class CW_Model:
    def __init__(self, size):
        from cw_grid import Grid
        
        self.__grid_size = size
        self.__grid = Grid(size)
        
        self.__grid.generate_layout(ratio=3.6, seed=3)
        
        self.__selected_cell = None
        self.__selected_direction = 'A' # A or D, defaults to A

    def change_selection(self, new_r, new_c, new_dir='A'):        
        # check if clicked away, (-1, -1)
        if new_r == new_c == -1: 
            self.__selected_cell = None
            self.__selected_direction = 'A'
        
        # check if clicked on the same cell as already selected, if can change direction then do so
        elif self.__selected_cell == (new_r, new_c):
            if self.__grid.is_cell_corner((new_r, new_c)): self.__flip_selected_direction()
        
        # if new selection is in the same word, keep the direction
        elif (new_r, new_c) in self.get_cells_in_selected_word():
            self.__selected_cell = (new_r, new_c)
        
        # if new selection is corner, defaults to across, unless came from the same down word
        elif self.__grid.is_cell_corner((new_r, new_c)):
            self.__selected_cell = (new_r, new_c)
            self.__selected_direction = new_dir
            
        # defaults direction to across if possible
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
        else:
            self.__selected_direction = 'A'

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