# cw_grid.py

from copy import deepcopy
from itertools import product
from random import randint
import word_funcs
from crossword_layout_gen import Crossword_layout_gen

EMPTY_CELL = 0
BLOCKED_CELL = 1

class Grid:
    def __init__(self, grid_size):
        self.__GRID_SIZE = grid_size
        
        """
        initialise grid:
        BLOCKED_CELL means cell is blocked
        EMPTY_CELL means cell is currently empty
        any letter means the cell has that character
        
        grid system is top-left 0/0, row then column
        """
        self.__grid = []
        self.empty_grid()
        
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
        
    """
    GETTERS
    """
    def get_grid(self):
        return self.__grid
    
    def get_grid_size(self):
        return self.__GRID_SIZE
        
    """
    METHODS
    """
    def empty_grid(self):
        self.__grid = [[EMPTY_CELL for __ in range(self.__GRID_SIZE)] for _ in range(self.__GRID_SIZE)]
        
    def clear_grid(self):
        newGrid = [[EMPTY_CELL if cell != BLOCKED_CELL else BLOCKED_CELL for cell in row] for row in self.__grid]
        self.__grid = deepcopy(newGrid)
        
    # use this method when initialising or a blocked cell is added / removed
    # this does NOT update the word lists
    # done to save time, no need to change this everytime a letter is changed
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
                while col_pointer != self.__GRID_SIZE and (next_char := self.__grid[row][col_pointer]) != BLOCKED_CELL:
                    word += str(next_char)
                    col_pointer += 1
                    
                self.__word_list_across[index+1] = word 
            # down
            if 'D' in direction:
                word = ''
                row_pointer = row
                while row_pointer != self.__GRID_SIZE and (next_char := self.__grid[row_pointer][col]) != BLOCKED_CELL:
                    word += str(next_char)
                    row_pointer += 1
                    
                self.__word_list_down[index+1] = word   
        
    def __change_cell(self, row, col, new_char):
        ## check if the parameters are valid
        # coordinate check
        if not (0 <= row < self.__GRID_SIZE and 0 <= col < self.__GRID_SIZE): raise Exception("coordinates out of bounds")
        # character check
        if not (len(new_char)==1 and (new_char.isalpha() or new_char == EMPTY_CELL or new_char == BLOCKED_CELL)): 
            raise Exception("not valid character")
        
        # get old character
        old_char = self.__grid[row][col]
        # update
        self.__grid[row][col] = new_char.upper() 
        
        # update numbered cells only if blocked cell added / removed
        if new_char == BLOCKED_CELL or old_char == BLOCKED_CELL: self.__update_numbered_cells()
        # update word lists no matter what
        self.__update_word_lists()
    
    # shouldn't be used
    def toggle_blocked_cell(self, row, col):
        if self.__grid[row][col] == BLOCKED_CELL: self.change_cell(row, col, EMPTY_CELL); return 1
        if self.__grid[row][col] == EMPTY_CELL: self.change_cell(row, col, BLOCKED_CELL); return 1
        
        raise Exception("something exists in this cell")
        
    # clear means no letters
    def __is_grid_clear(self):
        for row in self.__grid:
            for cell in row:
                if cell != BLOCKED_CELL and cell != EMPTY_CELL: return False
        return True
    
    # empty means no letters + no blocked cells
    def __is_grid_empty(self):
        for row in self.__grid:
            for cell in row:
                if cell != EMPTY_CELL: return False
        return True

    # checks if ALL the words in the grid are valid and completely filled
    def check_grid_words_validity(self):
        for across_word in self.__word_list_across.values():
            if not word_funcs.is_valid_word(across_word): return False
        for down_word in self.__word_list_down.values():
            if not word_funcs.is_valid_word(down_word): return False
        return True
        
    def generate_layout(self, symmetry=2, ratio=3, longest_word=13):
        if not self.__is_grid_empty(): raise Exception("The grid isn't empty")
        
        layout = Crossword_layout_gen(self.__GRID_SIZE, symmetry, ratio, longest_word)
        self.__grid = layout.generate_layout()

    '''
    DEBUGGING METHODS
    '''
    def print_grid(self):
        row_delim = '+-'*(self.__GRID_SIZE)+'+'
        output = row_delim+'\n'
        output += ('\n'+row_delim+'\n').join(['|'.join(['']+['#' if c else '.' for c in row]+['']) for row in self.__grid])
        output += '\n'+row_delim
        print(output)
        
    def print_numbered_cells(self):
        print(self.__numbered_cells)
    
    def print_word_lists(self):
        output_string = ""
        # across
        sorted_across = sorted(list(self.__word_list_across.items()), key=lambda kv_pair:kv_pair[0])
        output_string += '\n'.join([f"{number} across: {word}" for number, word in sorted_across])+'\n'
        # down
        sorted_down = sorted(list(self.__word_list_down.items()), key=lambda kv_pair:kv_pair[0])
        output_string += '\n'.join([f"{number} down: {word}" for number, word in sorted_down])

        print(output_string)
        
    def randomise_letters(self):
        from random import randint
        from string import ascii_uppercase
        for i in range(self.__GRID_SIZE):
            for j in range(self.__GRID_SIZE):
                self.__change_cell(i, j, ascii_uppercase[randint(0, 25)])

        
if __name__ == '__main__':
    
    test_grid = Grid(9)
    
    test_grid.generate_layout()

    # test_grid.print_grid()
    test_grid.print_grid()

