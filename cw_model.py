# cw_model.py

from cw_layout_filler import Crossword_Layout
from cw_autofill import Autofill
from app_settings import *

from grid import Grid

class CW_Model:
    def __init__(self, grid_size=None, grid_object=None):
        """
        if grid_size is passed, an empty grid of that size will be initialised
        if a grid object is passed, that object will be used
        """
        
        if (not grid_size and not grid_object) or (grid_size and grid_object): 
            raise Exception("Need to pass either a grid size or a Grid object")
        
        # initialise self.__grid
        if grid_object: self.__grid = grid_object
        else: self.__grid = Grid(grid_size)
        
        self.__GRID_SIZE = self.__grid.get_grid_size()
        
        self.__selected_cell = (-1, -1)
        self.__selected_direction = 'A' # default to across, so when an intersection is clicked, the across clue is higlighted first
                
    # layout related methods
    def flip_blocked_symmetry(self, row, col):
        self.__grid.flip_blocked_symmetry(row, col)

    def generate_layout(self, target_ratio, seed):
        if not self.is_grid_empty(): raise Exception("The grid isn't empty")
        self.__grid.set_grid(Crossword_Layout(self.__GRID_SIZE).generate_layout(self.__grid, target_ratio, seed))

    # clue writing related methods
    def enter_letter(self, letter):
        """
        letter takes in the letter, or BLOCKED_CELL if backspace
        """
        if not self.__selected_cell: return # no cell selected
        r, c = self.__selected_cell
        if self.__grid.get_letter_in_cell(r, c) == BLOCKED_CELL: return # selected cell is blocked
        
        # set letters moved
        if letter != EMPTY_CELL:
            d = 1
        elif self.__grid.get_letter_in_cell(r, c) == EMPTY_CELL:
            d = -1
        else:
            d = 0
        
        if self.__selected_direction == 'A':
            next_r, next_c = r, c+d
        elif self.__selected_direction == 'D':
            next_r, next_c = r+d, c
            
        if not(0 <= next_r <= self.__GRID_SIZE-1 and 0 <= next_c <= self.__GRID_SIZE-1) \
            or self.__grid.get_letter_in_cell(next_r, next_c) == BLOCKED_CELL or d == 0:
            next_r, next_c = r, c # this means the selected cell should not be changed
        
        if letter == EMPTY_CELL:    
            self.__grid.change_letter(next_r, next_c, EMPTY_CELL) # delete letter in the current selected cell (for natural typing)
        else:    
            self.__grid.change_letter(r, c, letter) # delete letter in the current selected cell (for natural typing)
            
        if (next_r != r) or (next_c !=c): 
            self.change_selection(next_r, next_c)
            
    def autofill(self, constraint):
        filler = Autofill(self.__grid.get_grid())
        solution = filler.fill(constraint)
        if solution: self.__grid.set_grid(solution); return True
        return False

    # selection related methods
    def change_selection(self, new_r, new_c, direction=None):        
        # case if deselect everything (-1, -1)
        if new_r == new_c == -1: 
            self.__selected_cell = None
            self.__selected_direction = 'A'
        
        # check if clicked on the same cell as already selected, if can change direction then do so
        elif self.__selected_cell == (new_r, new_c):
            if self.__is_cell_corner((new_r, new_c)): self.__flip_selected_direction()
        
        # if new selection is in the same word, keep the direction
        elif (new_r, new_c) in self.get_cells_in_selected_clue():
            self.__selected_cell = (new_r, new_c)
        
        # if new selection is corner, keep same direction
        elif self.__is_cell_corner((new_r, new_c)):
            self.__selected_cell = (new_r, new_c)
            if direction: self.__selected_direction = direction
            
        # only one direction
        else: 
            self.__selected_cell = (new_r, new_c)
            if self.__is_cell_in_word(self.__selected_cell, 'A'): 
                self.__selected_direction = 'A'
            elif self.__is_cell_in_word(self.__selected_cell, 'D'): 
                self.__selected_direction = 'D'
            else: 
                self.__selected_direction = 'A'
    
    def __flip_selected_direction(self):
        if self.__selected_direction == 'A': 
            self.__selected_direction = 'D'
        elif self.__selected_direction == 'D':
            self.__selected_direction = 'A'
    
    def get_selected_cell(self):
        return self.__selected_cell

    def get_selected_clue(self):
        if not self.__selected_cell: return None
        
        clues = self.__grid.clues_containing_cell(*self.__selected_cell)
        for clue in clues:
            if clue.direction == self.__selected_direction: return clue
        return None
    
    def get_cells_in_selected_clue(self):
        clue = self.get_selected_clue()
        if not clue: return []
        return clue.cells

    # general getters and setters and checks
    def get_grid_size(self):
        return self.__GRID_SIZE
    
    def get_grid_object(self):
        return self.__grid
    
    def get_grid(self):
        return self.__grid.get_grid()
    
    def set_grid(self, grid):
        self.__grid.set_grid(grid)
    
    def get_numbered_cells(self):
        return self.__grid.get_numbered_cells()
    
    def empty_grid(self):
        self.__grid.empty_grid()
        
    def clear_grid(self):
        self.__grid.clear_grid()
    
    def is_grid_empty(self):
        return self.__grid.is_grid_empty()
    
    def is_grid_clear(self):
        return self.__grid.is_grid_clear()

    def __is_cell_corner(self, cell):
        return self.__grid.is_cell_corner(cell)

    def __is_cell_in_word(self, cell, direction):
        return self.__grid.is_cell_in_word(cell, direction)

    def print_grid(self):
        print('\n'.join(['|'.join([' ' if not c else c for c in row]) for row in self.__grid]))
        
        