# cw_model.py

from cw_layout_filler import Crossword_Layout
from cw_autofill import Autofill
from app_info import *

from crossword import Crossword
from cw_clue import CW_Clue
from copy import deepcopy

class CW_Model:
    """
    Acts as the model in the MVC structure, managing the crossword data and selection state.

    Variables:
        __crossword (Crossword): The crossword object storing the grid and clue data.
        __GRID_SIZE (int): The size of the grid.
        __selected_cell (tuple[int, int] or None): The currently selected cell, or None if nothing is selected.
        __selected_direction (str): The current selection direction, either 'A' or 'D'.

    Methods:
        flip_blocked_symmetry: Toggles a cell between blocked and empty with symmetry.
        generate_layout: Generates a blocked cell layout on an empty grid.
        enter_letter: Types a letter into the selected cell and advances the selection.
        autofill: Fills the grid with words using the autofill algorithm.
        change_selection: Updates the selected cell and direction.
        get_selected_cell: Returns the currently selected cell.
        get_selected_clue: Returns the clue corresponding to the current selection.
        get_cells_in_selected_clue: Returns the cells belonging to the selected clue.
        get_crossword_object: Returns the underlying Crossword object.
        get_grid_size: Returns the grid size.
        get_grid: Returns the 2D grid.
        set_grid: Sets the grid to a new layout.
        get_numbered_cells: Returns the numbered cells.
        get_all_clues: Returns all clues.
        empty_grid: Resets the grid to fully empty.
        clear_grid: Removes all letters while preserving blocked cells.
        is_grid_empty: Returns whether the grid is completely empty.
        is_grid_clear: Returns whether the grid contains no letters.
    """
    def __init__(self, grid_size=None, title=None, crossword_object=None):
        """
        Initialises the model with either a new empty grid with the given grid size or an existing crossword object.

        Args:
            grid_size (int): The size of the grid to create.
            title (str): The title of the crossword, used when creating a new grid.
            crossword_object (Crossword): An existing crossword object to use directly.
        """
        if (not grid_size and not crossword_object) or (grid_size and crossword_object): 
            raise Exception("Need to pass either a grid size or a Grid object")
        
        # initialise self.__grid
        if crossword_object: self.__crossword = crossword_object
        else: self.__crossword = Crossword(grid_size, title)
        
        self.__GRID_SIZE = self.__crossword.get_grid_size()
        
        self.__selected_cell = (-1, -1)
        self.__selected_direction = 'A'
                
    # layout related methods
    def flip_blocked_symmetry(self, row, col, symmetry):
        """
        Flip a cell between blocked and empty, applying the given symmetry.

        Args:
            row (int): Row # of the cell to flip.
            col (int): Column # of the cell to flip.
            symmetry (int): Symmetry mode. 1 for no symmetry, 2 for 2-fold, 4 for 4-fold.
        """
        self.__crossword.flip_blocked_symmetry(row, col, symmetry)

    def generate_layout(self, target_ratio, seed, symmetry):
        """
        Generates a blocked cell layout and applies it to the grid.

        Args:
            target_ratio (float): The desired ratio of empty cells to blocked cells.
            seed (int): Random seed for reproducible layout generation.
            symmetry (int): Symmetry mode to apply when placing blocked cells.
        """
        self.__crossword.set_grid(Crossword_Layout(self.__GRID_SIZE).generate_layout(target_ratio, seed, symmetry))

    # clue writing related methods
    def enter_letter(self, letter):
        """
        Types a letter into the selected cell and advances the selection in the current direction. 
        If backspace, moves the selection back and clears the cell.

        Args:
            letter (str): The letter to enter, or EMPTY_CELL to delete.
        """
        if not self.__selected_cell: return
        r, c = self.__selected_cell
        if self.__crossword.get_letter_in_cell(r, c) == BLOCKED_CELL: return # selected cell is blocked
        
        # set letters moved
        if letter != EMPTY_CELL: d = 1
        elif self.__crossword.get_letter_in_cell(r, c) == EMPTY_CELL: d = -1
        else: d = 0
        
        if self.__selected_direction == 'A':
            next_r, next_c = r, c+d
        elif self.__selected_direction == 'D':
            next_r, next_c = r+d, c
            
        if not(0 <= next_r <= self.__GRID_SIZE-1 and 0 <= next_c <= self.__GRID_SIZE-1) \
            or self.__crossword.get_letter_in_cell(next_r, next_c) == BLOCKED_CELL or d == 0:
            next_r, next_c = r, c
        
        if letter == EMPTY_CELL:    
            self.__crossword.change_letter(next_r, next_c, EMPTY_CELL, True)
        else:    
            self.__crossword.change_letter(r, c, letter, True)
            
        if (next_r != r) or (next_c != c): 
            self.change_selection(next_r, next_c)
            
    def autofill(self, constraint):
        """
        Fills the grid with words using the autofill algorithm. 
        Replaces the crossword with the solution if one is found.

        Args:
            constraint (int): The maximum number of attempts per clue before backtracking.

        Returns:
            bool: True if a solution was found, False otherwise.
        """
        filler = Autofill(self.__crossword)
        solution = filler.fill(constraint)
        if solution: self.__crossword = deepcopy(solution); return True
        return False

    def change_selection(self, new_r, new_c, direction=None):
        """
        Updates the selected cell and direction. 
        Handles direction flipping when the same corner cell is clicked again
        Keeps the same direction when moving within the same word.

        Args:
            new_r (int): Row # of the new selection.
            new_c (int): Column # of the new selection.
            direction (str, optional): Direction to force the selection to. If None, direction is inferred from the cell's context.
        """
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
        """
        Flips the selected direction between 'A' and 'D'.
        """
        self.__selected_direction = CW_Clue.other_direction(self.__selected_direction)
    
    def get_selected_cell(self):
        """
        Returns the currently selected cell.

        Returns:
            tuple[int, int] or None: The (row, col) of the selected cell, or None if nothing is selected.
        """
        return self.__selected_cell

    def get_selected_clue(self):
        """
        Returns the clue corresponding to the currently selected cell and direction.

        Returns:
            CW_Clue or None: The selected clue, or None if no cell is selected or no matching clue exists.
        """
        if not self.__selected_cell: return None
        
        clues = self.__crossword.clues_containing_cell(*self.__selected_cell)
        for clue in clues:
            if clue.direction == self.__selected_direction: return clue
        return None
    
    def get_cells_in_selected_clue(self):
        """
        Returns the list of cells belonging to the currently selected clue.

        Returns:
            list[tuple[int, int]]: List of (row, col) positions in the selected clue, or an empty list if no clue is selected.
        """
        clue = self.get_selected_clue()
        if not clue: return []
        return clue.cells

    """Getters, setters and checks"""
    def get_grid_size(self):
        """
        Returns the size of the grid.

        Returns:
            int: The number of rows/columns in the grid.
        """
        return self.__GRID_SIZE
    
    def get_crossword_object(self):
        """
        Returns the Crossword object used in the model.

        Returns:
            Crossword: The crossword object managed by this model.
        """
        return self.__crossword
    
    def get_grid(self):
        """
        Returns the grid as a 2D list.

        Returns:
            list[list[str]]: The current grid.
        """
        return self.__crossword.get_grid()
    
    def set_grid(self, grid):
        """
        Sets the grid to a new layout.

        Args:
            grid (list[list[str]]): What the grid should be set to.
        """
        self.__crossword.set_grid(grid)
    
    def get_numbered_cells(self):
        """
        Returns the list of numbered cells in the grid.

        Returns:
            list[tuple[int, int, str]]: List of (row, col, direction) tuples.
        """
        return self.__crossword.get_numbered_cells()
    
    def get_all_clues(self):
        """
        Returns all clues in the crossword.

        Returns:
            list[CW_Clue]: List of all clues.
        """
        return self.__crossword.get_all_clues()
    
    def empty_grid(self):
        """
        Resets all cells in the grid to empty, including blocked cells.
        """
        self.__crossword.empty_grid()
        
    def clear_grid(self):
        """
        Removes all letters from the grid while preserving blocked cells.
        """
        self.__crossword.clear_grid()
    
    def is_grid_empty(self):
        """
        Returns whether the grid is completely empty.

        Returns:
            bool: True if all cells are empty, False otherwise.
        """
        return self.__crossword.is_grid_empty()
    
    def is_grid_clear(self):
        """
        Returns whether the grid contains no letters.

        Returns:
            bool: True if all cells are either empty or blocked, False otherwise.
        """
        return self.__crossword.is_grid_clear()

    def get_errors(self):
        """
        Method used during editing the layout to display errors, if any
        """
        return self.__crossword.get_errors()

    def __is_cell_corner(self, cell):
        """
        Returns whether the given cell belongs to both an across and a down word.

        Args:
            cell (tuple[int, int]): The (row, col) position to check.

        Returns:
            bool: True if the cell is a corner, False otherwise.
        """
        return self.__crossword.is_cell_checked(cell)

    def __is_cell_in_word(self, cell, direction):
        """
        Returns whether the given cell is part of a word in the specified direction.

        Args:
            cell (tuple[int, int]): The (row, col) cell to check.
            direction (str): The direction to check, either 'A' or 'D'.

        Returns:
            bool: True if the cell is part of a word in the given direction, False otherwise.
        """
        return self.__crossword.is_cell_in_word(cell, direction)

    """Used for debugging"""
    def print_grid(self):
        """
        Prints a text representation of the current grid to the console.
        """
        print('\n'.join(['|'.join([' ' if not c else c for c in row]) for row in self.__crossword]))
