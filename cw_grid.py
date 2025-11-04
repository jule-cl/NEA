# cw_grid.py

from copy import deepcopy
from itertools import product
from cw_layout_filler import Crossword_Layout
from app_settings import *

EMPTY_CELL = ""
BLOCKED_CELL = BLOCKED_CELL

class Grid:
    def __init__(self, grid_size):
        """
        initialise grid:
        BLOCKED_CELL means cell is blocked
        EMPTY_CELL means cell is currently empty
        any letter means the cell has that character
        
        grid system is top-left 0/0, row then column
        there IS NO border
        """
        self.__GRID_SIZE = grid_size
        self.__grid = []
        self.empty_grid()
        
        # elements are tuples that take the form 
        # (row, col, direction)
        # direction is 'AD', 'A', or 'D'
        self.__numbered_cells = []
        self.__update_numbered_cells()

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
        
    # use this method when initialising or a blocked cell is added / removed
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

    def toggle_blocked(self, row, col, sym):
        self.__flip_blocked(row, col)
        target = self.__grid[row][col]
        
        if sym == 2:
            self.__flip_blocked(self.__GRID_SIZE-1-row, self.__GRID_SIZE-1-col, target)
            
        if sym == 4:
            self.__flip_blocked(self.__GRID_SIZE-1-row, self.__GRID_SIZE-1-col, target)
            self.__flip_blocked(col, self.__GRID_SIZE-1-row, target)
            self.__flip_blocked(self.__GRID_SIZE-1-col, row, target)
        
        self.__update_numbered_cells()
        
    # only one cell
    def __flip_blocked(self, row, col, target=None):
        if target == None:
            if self.__grid[row][col] == EMPTY_CELL: self.__grid[row][col] = BLOCKED_CELL
            elif self.__grid[row][col] == BLOCKED_CELL: self.__grid[row][col] = EMPTY_CELL
        else:
            self.__grid[row][col] = target

    def generate_layout(self, symmetry=2, ratio=3.2, longest_word=13, seed=None):
        if not self.is_grid_empty(): raise Exception("The grid isn't empty")
        self.__grid = Crossword_Layout(self.__grid).generate_layout(symmetry, ratio, longest_word, seed)
        self.__update_numbered_cells()

    def get_grid(self):
        return self.__grid

    def set_grid(self, grid):
        if len(grid) != self.__GRID_SIZE: raise Exception("something's wrong")
        self.__grid = grid
        self.__layout.set_grid(grid)
        self.__update_numbered_cells()

    def is_cell_corner(self, cell):
        return self.is_cell_in_word(cell, 'A') and self.is_cell_in_word(cell, 'D')

    def is_cell_in_word(self, cell, dir):
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
        
    def get_numbered_cells(self):
        return self.__numbered_cells
        
    def print_grid(self):
        print('\n'.join(['|'.join([' ' if not c else c for c in row]) for row in self.__grid]))
        
if __name__ == '__main__':
    
    test_grid = Grid(9)
    
    test_grid.generate_layout(ratio=3.6, seed=3)

    test_grid.print_grid()

