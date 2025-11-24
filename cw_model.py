# cw_model.py

from cw_layout_filler import Crossword_Layout
from cw_autofill import Autofill
from app_settings import *
from copy import deepcopy
from itertools import product

class CW_Model:
    def __init__(self, grid_size):
        """
        selected_cell: (int, int)
        selected_direction: "A" / "D"
        """
        
        self.__GRID_SIZE = grid_size
        self.__grid = []
        self.empty_grid()
        
        self.__symmetry = 2 # defaults to 2-fold
                
        self.__selected_cell = None
        self.__selected_direction = 'A' # A or D, defaults to A
        
        self.__numbered_cells = []
        self.__update_numbered_cells()
                
    # layout related methods
    def __update_numbered_cells(self):
        self.__numbered_cells = []
        for row, col in product(range(self.__GRID_SIZE), repeat=2):
            # check if cell should be numbered
            direction = ""
            # already blocked
            if self.__grid[row][col] == BLOCKED_CELL: continue
            # across
            if col == self.__GRID_SIZE-1: pass
            elif (self.__grid[row][col-1] == BLOCKED_CELL or col == 0) and self.__grid[row][col+1] != BLOCKED_CELL: direction += 'A'
            # down
            if row == self.__GRID_SIZE-1: pass
            elif (self.__grid[row-1][col] == BLOCKED_CELL or row == 0) and self.__grid[row+1][col] != BLOCKED_CELL: direction += 'D'
            
            # add to list if exists
            if direction: self.__numbered_cells.append((row, col, direction))

    def toggle_blocked(self, row, col):
        self.__flip_blocked(row, col)
        target = self.__grid[row][col]
        
        if self.__symmetry == 2:
            self.__flip_blocked(self.__GRID_SIZE-1-row, self.__GRID_SIZE-1-col, target)
            
        if self.__symmetry == 4:
            self.__flip_blocked(self.__GRID_SIZE-1-row, self.__GRID_SIZE-1-col, target)
            self.__flip_blocked(col, self.__GRID_SIZE-1-row, target)
            self.__flip_blocked(self.__GRID_SIZE-1-col, row, target)
        
        self.__update_numbered_cells()
        
    def __flip_blocked(self, row, col, target=None): # flip for one cell
        if target == None:
            if self.__grid[row][col] == EMPTY_CELL: self.__grid[row][col] = BLOCKED_CELL
            elif self.__grid[row][col] == BLOCKED_CELL: self.__grid[row][col] = EMPTY_CELL
        else:
            self.__grid[row][col] = target

    def generate_layout(self, symmetry, ratio, longest_word, seed):
        if not self.is_grid_empty(): raise Exception("The grid isn't empty")
        self.__grid = Crossword_Layout(self.__GRID_SIZE).generate_layout(symmetry, ratio, longest_word, seed)
        self.__update_numbered_cells()

    # clue writing related methods
    def enter_letter(self, letter):
        if not self.__selected_cell: return # no cell selected
        r, c = self.__selected_cell
        if self.__grid[r][c] == BLOCKED_CELL: return # selected cell is blocked
        
        self.__grid[r][c] = letter.upper() # overwrite letter in grid
        
        if self.__selected_direction == 'A':
            new_r, new_c = r, c+1
        elif self.__selected_direction == 'D':
            new_r, new_c = r+1, c
            
        if not(0 <= new_r <= self.__GRID_SIZE-1 and 0 <= new_c <= self.__GRID_SIZE-1) \
            or self.__grid[new_r][new_c] == BLOCKED_CELL:
            return # this means the selected cell should not be changed
        
        # change the selected cell
        self.change_selection(new_r, new_c)
        
    def backspace_clicked(self):
        if not self.__selected_cell: return # no cell selected
        r, c = self.__selected_cell
        if self.__grid[r][c] == BLOCKED_CELL: return # selected cell is blocked
        
        self.__grid[r][c] = EMPTY_CELL # clear letter in grid: this method will still function if the selected cell is empty
        
        if self.__selected_direction == 'A':
            new_r, new_c = r, c-1
        elif self.__selected_direction == 'D':
            new_r, new_c = r-1, c
            
        if not(0 <= new_r <= self.__GRID_SIZE-1 and 0 <= new_c <= self.__GRID_SIZE-1) \
            or self.__grid[new_r][new_c] == BLOCKED_CELL:
            return # this means the selected cell should not be changed
        
        # change the selected cell
        self.change_selection(new_r, new_c)

    def autofill(self, constraint):
        if not self.is_grid_clear(): raise Exception("The grid isn't clear")
        filler = Autofill(self.__grid)
        solution = filler.fill(constraint)
        if solution: self.__grid = solution; return True
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
        elif (new_r, new_c) in self.get_cells_in_selected_word():
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

    def get_cells_in_selected_word(self):
        if not self.__selected_cell: return []
        
        if self.__selected_direction == 'A':
            drow, dcol = 0, 1
        elif self.__selected_direction == 'D':
            drow, dcol = 1, 0
            
        all_cells = set()
        for direction in [1, -1]: # forwards / backwards
            test_row, test_col = self.__selected_cell
            while 0 <= test_row <= self.__GRID_SIZE-1 and 0 <= test_col <= self.__GRID_SIZE-1:
                if self.__grid[test_row][test_col] == BLOCKED_CELL: break
                all_cells.add((test_row, test_col))
                test_row += drow*direction
                test_col += dcol*direction
                
        return all_cells

    # general getters and setters and checks
    def get_grid_size(self):
        return self.__GRID_SIZE
    
    def get_grid(self):
        return self.__grid
    
    def set_grid(self, grid):
        if len(grid) != self.__GRID_SIZE: raise Exception("something's wrong")
        self.__grid = grid 
        self.__update_numbered_cells()
    
    def get_numbered_cells(self):
        return self.__numbered_cells
    
    def empty_grid(self):
        self.__grid = [[EMPTY_CELL]*self.__GRID_SIZE for _ in range(self.__GRID_SIZE)]
        self.__update_numbered_cells()
        
    def clear_grid(self):
        newGrid = [[EMPTY_CELL if cell != BLOCKED_CELL else BLOCKED_CELL for cell in row] for row in self.__grid]
        self.__grid = deepcopy(newGrid)
    
    def is_grid_empty(self):
        for row in self.__grid:
            for cell in row:
                if cell != EMPTY_CELL: return False
        return True
    
    def is_grid_clear(self):
        for row in self.__grid:
            for cell in row:
                if not(cell == EMPTY_CELL or cell == BLOCKED_CELL): return False
        return True

    def __is_cell_corner(self, cell):
        return self.__is_cell_in_word(cell, 'A') and self.__is_cell_in_word(cell, 'D')

    def __is_cell_in_word(self, cell, dir):
        row, col = cell
        if self.__grid[row][col] == BLOCKED_CELL: return False
        # across check
        if dir == 'A':
            if col != 0 and self.__grid[row][col-1] != BLOCKED_CELL: return True
            if col != self.__GRID_SIZE-1 and self.__grid[row][col+1] != BLOCKED_CELL: return True
            return False
        # down check
        if dir == 'D':
            if row != 0 and self.__grid[row-1][col] != BLOCKED_CELL: return True
            if row != self.__GRID_SIZE-1 and self.__grid[row+1][col] != BLOCKED_CELL: return True
            return False
        raise Exception("direction invalid")
        
    def print_grid(self):
        print('\n'.join(['|'.join([' ' if not c else c for c in row]) for row in self.__grid]))
        
        