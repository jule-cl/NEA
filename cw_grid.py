# cw_grid.py

from copy import deepcopy
from itertools import product
from random import randint
import word_funcs

class Grid:
    def __init__(self, grid_size):
        self.__grid_size = grid_size
        
        """
        initialise grid:
        '-' means cell is blocked
        '.' means cell is currently empty
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
        return self.__grid_size
        
    """
    METHODS
    """
    def empty_grid(self):
        self.__grid = [['.' for __ in range(self.__grid_size)] for _ in range(self.__grid_size)]
        
    def clear_grid(self):
        newGrid = [['.' if cell != '-' else '-' for cell in row] for row in self.__grid]
        self.__grid = deepcopy(newGrid)
        
    # use this method when initialising or a blocked cell is added / removed
    # this does NOT update the word lists
    # done to save time, no need to change this everytime a letter is changed
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
                while col_pointer != self.__grid_size and (next_char := self.__grid[row][col_pointer]) != '-':
                    word += next_char
                    col_pointer += 1
                    
                self.__word_list_across[index+1] = word 
            # down
            if 'D' in direction:
                word = ''
                row_pointer = row
                while row_pointer != self.__grid_size and (next_char := self.__grid[row_pointer][col]) != '-':
                    word += next_char
                    row_pointer += 1
                    
                self.__word_list_down[index+1] = word   
        
    def change_cell(self, row, col, new_char):
        ## check if the parameters are valid
        # coordinate check
        if not (0 <= row < self.__grid_size and 0 <= col < self.__grid_size): raise Exception("coordinates out of bounds")
        # character check
        if not (len(new_char)==1 and (new_char.isalpha() or new_char in '.-')): raise Exception("not valid character")
        
        # get old character
        old_char = self.__grid[row][col]
        # update
        self.__grid[row][col] = new_char.upper() 
        
        # update numbered cells only if blocked cell added / removed
        if new_char == '-' or old_char == '-': self.__update_numbered_cells()
        # update word lists no matter what
        self.__update_word_lists()
        
    # clear means no letters
    def __is_grid_clear(self):
        for row in self.__grid:
            for cell in row:
                if cell != '-' and cell != '.': return False
        return True
    
    # empty means no letters + no blocked cells
    def __is_grid_empty(self):
        for row in self.__grid:
            for cell in row:
                if cell != '.': return False
        return True

    # checks if ALL the words in the grid are valid and completely filled
    def check_grid_words_validity(self):
        for across_word in self.__word_list_across.values():
            if not word_funcs.is_valid_word(across_word): return False
        for down_word in self.__word_list_down.values():
            if not word_funcs.is_valid_word(down_word): return False
        return True
        
    def randomise_blocked_cells(self):
        if self.__grid_size % 2 == 0: return -1 # weird grid size
        if not self.__is_grid_empty(): return -1 # grid has stuff in it, need to be empty
        
        filling_type = randint(0, 3)
        horizontal = filling_type & 1
        vertical = (filling_type & 2)//2
        
        for row in range(horizontal, self.__grid_size, 2):
            for col in range(vertical, self.__grid_size, 2):
                self.change_cell(row, col, '-')
        
    '''
    DEBUGGING METHODS
    '''
    def print_grid(self):
        row_delim = '\n'+'-'*(2*self.__grid_size-1)+'\n'
        print(row_delim.join(['|'.join(row) for row in self.__grid]))
    
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
        for i in range(self.__grid_size):
            for j in range(self.__grid_size):
                self.change_cell(i, j, ascii_uppercase[randint(0, 25)])

        
if __name__ == '__main__':
    
    test_grid = Grid(5)
    
    # random letters (for now)
    test_grid.randomise()
            
    test_grid.change_cell(1, 1, '-')
    test_grid.change_cell(1, 3, '-')
    test_grid.change_cell(3, 1, '-')
    test_grid.change_cell(3, 3, '-')
            
    # test_grid.print_grid()
    test_grid.print_word_lists()

