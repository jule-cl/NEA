# cw_layout_filler.py

# filling blocked cells in grid

from itertools import product
from random import randint, choice
from copy import deepcopy
from collections import deque
from bitboard import Bitboard
from app_info import *

O_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

class Crossword_Layout:
    """
    Generates and validates a blocked cell layout for a crossword grid.
    The grid is represented with a 1-cell border of blocked cells on all sides,
    so the actual area is (1,1) to (GRID_SIZE, GRID_SIZE).

    Variables:
        __GRID_SIZE (int): The size of the playable grid area.
        __grid (list[list[str]]): 2D grid including the blocked border.
        __blocked_cells (list[tuple[int, int]]): All currently blocked cell positions.
        __empty_cells (list[tuple[int, int]]): All currently empty cell positions.
        __grid_bitboard (Bitboard): Bitboard representation of the blocked cells for fast validity checks.
        __number_of_blocked_cells (int): Count of blocked cells in the playable area.

    Methods:
        empty_grid: Resets the grid to fully empty with only border cells blocked.
        set_grid: Loads an existing grid layout into this instance.
        generate_layout: Generates a blocked cell layout for the given target ratio and symmetry.
        get_borderless_grid: Returns the grid without the border cells.
        get_blocked: Returns the list of blocked cell positions.
        print_grid: Prints a text representation of the grid to the console.
    """
    
    def __init__(self, size):
        """
        Initialises the Crossword_Layout instance and sets up an empty grid.

        Args:
            size (int): The size of the actual grid. Must be provided before calling any generation methods.
        """
        self.__GRID_SIZE = size
        
    def __flip_cell(self, row, col):
        """
        Flip a single cell between blocked and empty, updating all related state.

        Args:
            row (int): Row # of the cell to toggle.
            col (int): Column # of the cell to toggle.
        """
        if self.__grid[row][col] == BLOCKED_CELL:
            self.__grid[row][col] = EMPTY_CELL
            self.__grid_bitboard.remove_cell(row, col)
            self.__blocked_cells.remove((row, col))
            self.__empty_cells.append((row, col))
            self.__number_of_blocked_cells -= 1
            
        elif self.__grid[row][col] == EMPTY_CELL:
            self.__grid[row][col] = BLOCKED_CELL
            self.__grid_bitboard.add_cell(row, col)
            self.__empty_cells.remove((row, col))
            self.__blocked_cells.append((row, col))
            self.__number_of_blocked_cells += 1
            
    def __flip_cell_sym(self, row, col, sym):
        """
        Flips a cell and all its symmetrically corresponding cells.

        Args:
            row (int): Row # of the original cell.
            col (int): Column # of the original cell.
            sym (int): Symmetry mode. 2 for 180-degree rotational symmetry, 4 for 4-fold symmetry.
        """
        for t_row, t_col in self.__get_cells_in_sym(row, col, sym):
            self.__flip_cell(t_row, t_col)

    def __get_cells_in_sym(self, row, col, sym):
        """
        Returns the set of cells corresponding to the given cell under the specified symmetry.

        Args:
            row (int): Row index of the primary cell.
            col (int): Column index of the primary cell.
            sym (int): Symmetry mode. 2 for 180-degree rotational symmetry, 4 for 4-fold symmetry.

        Returns:
            set[tuple[int, int]]: Set of (row, col) positions including the original cell
                                  and all symmetric counterparts.
        """
        cells = set([(row, col)])
        if sym == 2:
            cells.add((self.__GRID_SIZE+1-row, self.__GRID_SIZE+1-col))
        if sym == 4:
            cells.add((self.__GRID_SIZE+1-row, self.__GRID_SIZE+1-col))
            cells.add((col, self.__GRID_SIZE+1-row))
            cells.add((self.__GRID_SIZE+1-col, row))
        return cells

    def empty_grid(self):
        """
        Resets the grid to a fully empty state, with only the border cells blocked.
        Reinitialises all related state including blocked cells, empty cells, and the bitboard.
        """
        self.__grid = [[BLOCKED_CELL]*(self.__GRID_SIZE+2) if row == 0 or row == self.__GRID_SIZE+1
                       else [BLOCKED_CELL]+[EMPTY_CELL]*self.__GRID_SIZE+[BLOCKED_CELL] for row in range(self.__GRID_SIZE+2)]

        self.__blocked_cells = []
        for i in range(self.__GRID_SIZE+1):
            self.__blocked_cells += [(i, 0), (0, i+1), (self.__GRID_SIZE+1, i), (i+1, self.__GRID_SIZE+1)]
        self.__empty_cells = [(r, c) for r, c in product(range(1, self.__GRID_SIZE+1), repeat=2)]
        self.__grid_bitboard = Bitboard(deepcopy(self.__blocked_cells), self.__GRID_SIZE+2)
        self.__number_of_blocked_cells = 0

    def set_grid(self, grid):
        """
        Loads an existing grid layout into this instance by resetting the blocked cell positions.

        Args:
            grid (list[list[str]]): A 2D grid without border cells to load.
        """
        self.empty_grid()
        for row_num, row in enumerate(grid):
            for col_num, cell in enumerate(row):
                if cell == BLOCKED_CELL: 
                    self.__flip_cell(row_num+1, col_num+1)

    def generate_layout(self, target_ratio, base, symmetry):
        """
        Generates a blocked cell layout by first placing a regular base pattern.
        Then randomly adding blocked cells until the target ratio is reached.
        Checks if the grid is valid after each addition and reverting invalid placements.

        Args:
            target_ratio (float): The desired ratio of empty cells to blocked cells.
            base (int or None): The base pattern offset (0-3). If None, a suitable base is chosen randomly based on the symmetry mode.
            symmetry (int): Symmetry mode to apply when placing blocked cells.

        Returns:
            list[list[str]]: The generated grid without border cells.
        """
        self.empty_grid() # should already be empty, this will also initialise variables
        
        if base == None: 
            if symmetry == 4: base = choice([0, 3])
            else: base = randint(0, 3)

        # generate base
        col_offset = int(base & 1 == 1)+1
        row_offset = int(base & 2 == 2)+1
        
        for row in range(row_offset, self.__GRID_SIZE+1, 2):
            for col in range(col_offset, self.__GRID_SIZE+1, 2):
                self.__flip_cell(row, col)
                
        target_blocked = (self.__GRID_SIZE**2) / target_ratio
        
        banned_cells = []
        attempts = 0
        while self.__number_of_blocked_cells-4*(self.__GRID_SIZE+1) <= target_blocked and attempts < 20:
            # pick random cell
            t_row, t_col = randint(1, self.__GRID_SIZE), randint(1, self.__GRID_SIZE)
            attempts += 1
            if self.__grid[t_row][t_col] == BLOCKED_CELL: continue
            if (t_row, t_col) in banned_cells: continue
            self.__flip_cell_sym(t_row, t_col, symmetry)
            
            if not self.__grid_valid():
                self.__flip_cell_sym(t_row, t_col, symmetry)
                banned_cells += self.__get_cells_in_sym(t_row, t_col, symmetry)
                
        return [row[1:-1] for row in self.__grid[1:-1]]
           
    def __grid_valid(self):
        """
        Checks whether the current grid satisfies all crossword validity constraints.

        Returns:
            bool: True if the grid passes all checks, False otherwise.
        """
        return self.__connectivity_check() and self.__two_letter_word_check()[0]\
                and self.__two_unch_check()[0] and self.__block_clump_check()[0]
                        
    def __connectivity_check(self):
        """
        Checks that all empty cells in the grid are connected.
        Uses a breadth-first search starting from the first empty cell.

        Returns:
            bool: True if all empty cells are reachable from each other, False otherwise.
        """
        self.__visited = []
        to_visit = deque([self.__empty_cells[0]])
        
        while to_visit:
            current = to_visit.popleft()
            
            for d_row, d_col in O_DIRECTIONS:
                new_row, new_col = current[0]+d_row, current[1]+d_col
                
                if (new_row, new_col) in self.__visited: continue
                if (new_row, new_col) in to_visit: continue
                if self.__grid[new_row][new_col] == BLOCKED_CELL: continue
                if not (1 <= new_row <= self.__GRID_SIZE and 1 <= new_col <= self.__GRID_SIZE): continue
                
                to_visit.append((new_row, new_col))
                
            self.__visited.append(current)
            
        return len(self.__visited) == len(self.__empty_cells)
                
    def __two_letter_word_check(self):
        """
        Checks that no word in the grid is exactly two letters long.

        Returns:
            bool: True if no two-letter words exist, False otherwise.
        """
        overlay = Bitboard([(i, 0) for i in range(4)], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(0, 0), (3, 0)], self.__GRID_SIZE+2)
        for row in range(self.__GRID_SIZE-1):
            for col in range(1, self.__GRID_SIZE+1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False, [(row+1, col), (row+2, col)]
                
        overlay = Bitboard([(0, i) for i in range(4)], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(0, 0), (0, 3)], self.__GRID_SIZE+2)
        for row in range(1, self.__GRID_SIZE+1):
            for col in range(self.__GRID_SIZE-1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False, [(row, col+1), (row, col+2)]
                
        return True, []
        
    def __two_unch_check(self):
        """
        Checks that no two consecutive unchecked cells appear in any word. 

        Returns:
            bool: True if no two consecutive unchecked cells exist, False otherwise.
        """
        overlay = Bitboard([(i, j) for i in [0, 1] for j in [0, 1, 2]], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(i, j) for i in [0, 1] for j in [0, 2]], self.__GRID_SIZE+2)
        for row in range(self.__GRID_SIZE+1):
            for col in range(self.__GRID_SIZE):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False, [(row, col+1), (row+1, col+1)]
             
        overlay = Bitboard([(j, i) for i in [0, 1] for j in [0, 1, 2]], self.__GRID_SIZE+2)
        result_if_true = Bitboard([(j, i) for i in [0, 1] for j in [0, 2]], self.__GRID_SIZE+2)
        for row in range(self.__GRID_SIZE):
            for col in range(self.__GRID_SIZE+1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
                new_result = deepcopy(result_if_true)
                new_result.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_result.get_bit_board():
                    return False, [(row+1, col), (row+1, col+1)]
                
        return True, []

    def __block_clump_check(self):
        """
        Checks that no 2x2 cluster of blocked cells exists in the grid.

        Returns:
            bool: True if no 2x2 blocked clusters exist, False otherwise.
        """
        overlay = Bitboard([(i, j) for i in [0, 1] for j in [0, 1]], self.__GRID_SIZE+2)
        for row in range(1, self.__GRID_SIZE-1):
            for col in range(1, self.__GRID_SIZE-1):
                new_overlay = deepcopy(overlay)
                new_overlay.translate_bitboard(row, col)
    
                if new_overlay.get_bit_board() & self.__grid_bitboard.get_bit_board() == new_overlay.get_bit_board():
                    return False, [(row, col), (row, col+1), (row+1, col), (row+1, col+1)]
                
        return True, []
    
    def get_errors(self):
        """
        This method is used to find errors which will be displayed on the grid.
        
        Returns:
            tuple[str, list[tuple[int, int]]] or None
            If there is an error, the error the relevant cells are return. Otherwise None.
        """
        errors = {}
        
        # all cell row and column # needs to subtracted by 1, as the numbering is indexed from 1 here and not anywhere else
        if not self.__connectivity_check(): 
            cell1, cell2 = min(list(set(self.__empty_cells).difference(self.__visited))), min(self.__visited)
            errors[ERRORS.CONNECTIVITY] = [(cell1[0]-1, cell1[1]-1), (cell2[0]-1, cell2[1]-1)]
        word_length = self.__two_letter_word_check()
        if not word_length[0]: errors[ERRORS.WORD_LEN] = [(r-1, c-1) for r, c in word_length[1]]
        two_unch = self.__two_unch_check()
        if not two_unch[0]: errors[ERRORS.TWO_UNCH] = [(r-1, c-1) for r, c in two_unch[1]]
        block_clump = self.__block_clump_check()
        if not block_clump[0]: errors[ERRORS.BLOCK_CLUMP] = [(r-1, c-1) for r, c in block_clump[1]]
        
        return errors
    
    """GETTERS""" 
    def get_borderless_grid(self):
        """
        Returns the grid with the border cells stripped, giving just the actual grid.

        Returns:
            list[list[str]]: The grid without border cells.
        """
        final_grid = [row[1:-1] for row in self.__grid[1:-1]]
        return final_grid
    
    def get_blocked(self):
        """
        Returns the list of all currently blocked cell positions.

        Returns:
            list[tuple[int, int]]: List of (row, col) positions of blocked cells.
        """
        return self.__blocked_cells
      
    """Used for debugging"""
    def print_grid(self):
        """
        Prints a text representation of the grid to the console.
        """
        row_delim = '\n'+'-+'*(self.__GRID_SIZE+1)+'-'+'\n'
        print(row_delim.join(['|'.join(['#' if c else '.' for c in row]) for row in self.__grid]))
        
    def print_numbered_cells(self):
        """
        Prints the list of numbered cells to the console.
        """
        print(self.__numbered_cells)
    
    def print_word_lists(self):
        """
        Prints all across and down word lists to the console, sorted by clue number.
        """
        output_string = ""
        # across
        sorted_across = sorted(list(self.__word_list_across.items()), key=lambda kv_pair:kv_pair[0])
        output_string += '\n'.join([f"{number} across: {word}" for number, word in sorted_across])+'\n'
        # down
        sorted_down = sorted(list(self.__word_list_down.items()), key=lambda kv_pair:kv_pair[0])
        output_string += '\n'.join([f"{number} down: {word}" for number, word in sorted_down])

        print(output_string)
