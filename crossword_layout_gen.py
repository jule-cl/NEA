# crossword_layout_gen.py

# filling blocked cells in grid

from itertools import product
from copy import deepcopy
from collections import deque
from bitboard import Bitboard

EMPTY_CELL = 0
BLOCKED_CELL = 1

O_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

class Crossword_layout_gen:
    
    def __init__(self, size, symmetry=2, ratio=3.2, longest_word=13):
        # grid is at (1, 1) top-left, goes to (s, s) bottom-right, and (row, column)
        # boundary is r=0, r=s+1, c=0, c=s+1
        
        self.__grid = [[BLOCKED_CELL]*(size+2) if row == 0 or row == size+1
                       else [BLOCKED_CELL]+[EMPTY_CELL]*size+[BLOCKED_CELL] for row in range(size+2)]
        self.__GRID_SIZE = size
        
        if not self.__is_grid_empty(): raise Exception("the grid must be empty")

        if symmetry != 2 and symmetry != 4: raise Exception("grid symmetry is wrong")
        self.__SYMMETRY = symmetry
        self.__RATIO = ratio
        self.__LONGEST_WORD = longest_word
        
        self.__blocked_cells = []
        for i in range(self.__GRID_SIZE+1):
            self.__blocked_cells += [(i, 0), (0, i+1), (self.__GRID_SIZE+1, i), (i+1, self.__GRID_SIZE+1)]
        self.__empty_cells = [(r, c) for r, c in product(range(1, self.__GRID_SIZE+1), repeat=2)]
            
        self.__grid_bitboard = Bitboard(deepcopy(self.__blocked_cells), self.__GRID_SIZE+2)
                
    # empty means no letters
    def __is_grid_empty(self):
        for row in self.__grid[1:-1]:
            for cell in row[1:-1]:
                if cell != EMPTY_CELL: return False
        return True    

    def __flip_cell(self, row, col):
        if self.__grid[row][col] == BLOCKED_CELL:
            self.__grid[row][col] = EMPTY_CELL
            self.__grid_bitboard.remove_cell(row, col)
            self.__blocked_cells.remove((row, col))
            self.__empty_cells.append((row, col))
            
        elif self.__grid[row][col] == EMPTY_CELL:
            self.__grid[row][col] = BLOCKED_CELL
            self.__grid_bitboard.add_cell(row, col)
            self.__empty_cells.remove((row, col))
            self.__blocked_cells.append((row, col))
            
    def __flip_cell_sym(self, row, col):
        to_flip = set([(row, col), (self.__GRID_SIZE+1-row, self.__GRID_SIZE+1-col)])
        if self.__SYMMETRY == 4:
            to_flip.add((col, self.__GRID_SIZE+1-row))
            to_flip.add((self.__GRID_SIZE+1-col, row))
            
        for t_row, t_col in to_flip:
            self.__flip_cell(t_row, t_col)
  
    # should never be used, too inefficient
    def __update_bitboard(self):
        new_cells = []
        for row in range(self.__GRID_SIZE):
            for col in range(self.__GRID_SIZE):
                if self.__grid[row][col] == BLOCKED_CELL: new_cells.append((row, col))
                
        self.__grid_bitboard = Bitboard(new_cells, self.__GRID_SIZE+2)
           
    # TODO, still tweaking
    def generate_layout(self, seed=None):
        from random import randint
        if seed == None: seed = randint(1, 2^16)
        
        # generate base
        base = seed % 4
        row_offset = int(base & 1 == 1)+1
        col_offset = int(base & 2 == 2)+1
        
        for row in range(row_offset, self.__GRID_SIZE+1, 2):
            for col in range(col_offset, self.__GRID_SIZE+1, 2):
                self.__flip_cell(row, col)
                
        target_blocked = (self.__GRID_SIZE**2) / self.__RATIO
        
        if self.__GRID_SIZE > self.__LONGEST_WORD:
            for t_row in range((row_offset-1)^1+1, self.__GRID_SIZE//2+1, 2):
                t_col = randint(int(self.__GRID_SIZE/3), int(self.__GRID_SIZE*2/3))
                self.__flip_cell_sym(t_row, t_col)
                
                offset = 0
                while not self.__grid_valid():
                    self.__flip_cell_sym((t_row+offset-1)%self.__GRID_SIZE+1, t_col)
                    offset += 1
                    self.__flip_cell_sym((t_row+offset-1)%self.__GRID_SIZE+1, t_col)
               
        while len(self.__blocked_cells)-4*(self.__GRID_SIZE+1) <= target_blocked:
            t_row, t_col = randint(1, self.__GRID_SIZE), randint(1, self.__GRID_SIZE)
            
            if self.__grid[t_row][t_col] == BLOCKED_CELL: continue

            self.__flip_cell_sym(t_row, t_col)
            
            if not self.__grid_valid():
                self.__flip_cell_sym(t_row, t_col)
                
        return self.__grid
           
    def __grid_valid(self):
        return self.__two_letter_word_check() and self.__connectivity_check() \
                and self.__two_unch_check() and self.__block_clump_check()
                        
    def __connectivity_check(self):
        visited = []
        to_visit = deque([self.__empty_cells[0]])
        
        while to_visit:
            current = to_visit.popleft()
            
            for d_row, d_col in O_DIRECTIONS:
                new_row, new_col = current[0]+d_row, current[1]+d_col
                
                if (new_row, new_col) in visited: continue
                if (new_row, new_col) in to_visit: continue
                if self.__grid[new_row][new_col] == BLOCKED_CELL: continue
                
                to_visit.append((new_row, new_col))
                
            visited.append(current)
            
        return len(visited) == len(self.__empty_cells)
                
    def __two_letter_word_check(self):
        
        # vertical check
        overlay = Bitboard([(i, 0) for i in range(4)], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(0, 0), (3, 0)], self.__GRID_SIZE+2)
        for row in range(self.__GRID_SIZE-1):
            for col in range(1, self.__GRID_SIZE+1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False
                
        # horizontal check
        overlay = Bitboard([(0, i) for i in range(4)], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(0, 0), (0, 3)], self.__GRID_SIZE+2)
        for row in range(1, self.__GRID_SIZE+1):
            for col in range(self.__GRID_SIZE-1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False
                
        return True
        
    def __two_unch_check(self):
        
        # vertical check
        overlay = Bitboard([(i, j) for i in [0, 1] for j in [0, 1, 2]], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(i, j) for i in [0, 1] for j in [0, 2]], self.__GRID_SIZE+2)
        for row in range(self.__GRID_SIZE+1):
            for col in range(self.__GRID_SIZE):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False
             
        # horizontal check
        overlay = Bitboard([(j, i) for i in [0, 1] for j in [0, 1, 2]], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(j, i) for i in [0, 1] for j in [0, 2]], self.__GRID_SIZE+2)
        for row in range(self.__GRID_SIZE):
            for col in range(self.__GRID_SIZE+1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False
                
        return True

    def __block_clump_check(self):
        overlay = Bitboard([(i, j) for i in [0, 1] for j in [0, 1]], self.__GRID_SIZE+2)
        for row in range(self.__GRID_SIZE-1):
            for col in range(1, self.__GRID_SIZE+1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_overlay.get_bit_board():
                    return False
                
        return True
      
    def get_borderless_grid(self):
        final_grid = [row[1:-1] for row in self.__grid[1:-1]]
        return final_grid
    
    def get_blocked(self):
        return self.__blocked_cells
      
    ##------------
    # DEBUGGING
    ##------------
    def print_grid(self):
        row_delim = '\n'+'-+'*(self.__GRID_SIZE+1)+'-'+'\n'
        print(row_delim.join(['|'.join(['#' if c else '.' for c in row]) for row in self.__grid]))
        
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
        
        
if __name__ == '__main__':
    ## empty/block ratio of 3.2 looks nice
    filler = Crossword_layout_gen(size=9, ratio=3.2)
    
    filler.generate_layout()
    
    filler.print_grid()
    
    

    


    