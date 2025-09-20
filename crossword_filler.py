# crossword_filler.py

# filling words in grid

from itertools import product

EMPTY_CELL = 0
BLOCKED_CELL = 1

class Crossword_filler:
    
    def __init__(self, grid):
        self.__grid = grid
        self.__grid_size = len(grid)
        
        # elements are tuples that take the form 
        # (row, col, direction)
        # direction is 'AD', 'A', or 'D'
        # 0-indexed
        self.__numbered_cells = []
        self.__update_numbered_cells()
        
        # each key-value pair is in the form 
        # numbered cell: string
        # standard crossword indexing
        self.__word_list_across = {}
        self.__word_list_down = {}
        self.__update_word_lists()
        
    def __update_numbered_cells(self):
        self.__numbered_cells = []
        for row, col in product(range(self.__grid_size), repeat=2):
            # check if cell should be numbered
            direction = ""
            # already blocked
            if self.__grid[row][col] == '-': continue
            # across
            if col == self.__grid_size-1: pass
            elif (self.__grid[row][col-1] == '-' or col == 0) and self.__grid[row][col+1] != '-': direction += 'A'
            # down
            if row == self.__grid_size-1: pass
            elif (self.__grid[row-1][col] == '-' or row == 0) and self.__grid[row+1][col] != '-': direction += 'D'
            
            # add to list if exists
            if direction: self.__numbered_cells.append((row, col, direction))
        
    # use this method when a character is changed (no matter blocked or letter)
    # this uses the numbered cells, but does NOT update it
    # if using this after a blocked cell change, make sure to update numbered cells
    def __update_word_lists(self):
        self.__word_list_across = {}
        self.__word_list_down = {}
        
        for index, (row, col, direction) in enumerate(self.__numbered_cells):
            # across
            if 'A' in direction:
                word = ''
                col_pointer = col
                while col_pointer != self.__grid_size and (next_char := self.__grid[row][col_pointer]) != BLOCKED_CELL:
                    word += next_char
                    col_pointer += 1
                    
                self.__word_list_across[index+1] = word 
            # down
            if 'D' in direction:
                word = ''
                row_pointer = row
                while row_pointer != self.__grid_size and (next_char := self.__grid[row_pointer][col]) != BLOCKED_CELL:
                    word += next_char
                    row_pointer += 1
                    
                self.__word_list_down[index+1] = word  
                
    def print_grid(self):
        row_delim = '\n'+'-'*(2*self.__grid_size-1)+'\n'
        print(row_delim.join(['|'.join(['#' if c else '.' for c in row]) for row in self.__grid]))
                
                
if __name__ == '__main__':
    from time import time # for debugging
    start_time = time()
    
    size = 9
    
    from crossword_layout_gen import Crossword_layout_gen
    gen = Crossword_layout_gen(size)
    
    gen.generate_layout()
    grid_layout = gen.get_grid()
    
    filler = Crossword_filler(grid_layout)
    filler.print_grid()


