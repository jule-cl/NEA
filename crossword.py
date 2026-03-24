# crossword.py

from copy import deepcopy
from itertools import product
from datetime import date
import os
import json

from cw_clue import CW_Clue
from app_info import *

class Crossword:
    """
    Represents a crossword puzzle, storing the grid and all associated clues, as well as metadata.

    Variables:
        __GRID_SIZE (int): The fixed size of the grid (number of rows/columns).
        __grid (list[list[str]]): 2D list storing the contents of each cell.
        __numbered_cells (list[tuple[int, int, str]]): List of (row, col, direction) tuples for numbered cells.
        __all_clues (list[CW_Clue]): List of all clues derived from the current grid layout.
        __checked_cells (set[tuple[int, int]]): A set containing all checked cells.

    Methods:
        save: Serialises the crossword to a JSON file at the given filepath.
        load: Class method that deserialises a crossword from a JSON file.
        empty_grid: Resets all cells to empty.
        clear_grid: Removes all letters while preserving blocked cells.
        flip_blocked_symmetry: Toggles a cell between blocked and empty, applying symmetry.
        change_letter: Updates a single cell and all clues containing it.
        clues_containing_cell: Returns all clues that pass through a given cell.
        print_grid: Prints a text representation of the grid to the console.

    Getters:
        get_grid_size: Returns the grid size.
        get_grid: Returns the 2D grid list.
        get_all_clues: Returns the list of all clues.
        get_letter_in_cell: Returns the character at a given cell.
        get_numbered_cells: Returns the list of numbered cells.

    Checks:
        is_grid_empty: Returns True if all cells are empty.
        is_grid_clear: Returns True if all cells are either empty or blocked.
        is_cell_corner: Returns True if the cell belongs to both an across and down word.
        is_cell_in_word: Returns True if the cell is part of a word in the given direction.
    """
    def __init__(self, grid_size, title, created_date=str(date.today()), filename=""):
        ## META DATA
        self.__title = title
        self.__created_date = created_date
        self.__filename = filename
        
        self.__GRID_SIZE = grid_size
        self.__grid = [] # coordinates are 0-indexed
        self.__numbered_cells = [] # (row, col, direction)
        self.__checked_cells = set()
        self.__all_clues = []
        self.empty_grid()

    # saving / loading
    def save(self):
        """
        Serialises and saves the crossword to a JSON file in the saves folder.
        If the crossword has not been saved before, a new file is created and registered in the index.
        If the crossword has already been saved, the existing file is overwritten.
        """
        os.makedirs(SAVED_FOLDER, exist_ok=True)
        
        # if this crossword has not already been saved before, create new file TODO
        if not self.__filename:
            # create file
            self.__filename = f"{self.__title.replace(' ', '_')}_{self.__created_date}"
            filepath = os.path.join(SAVED_FOLDER, f"{self.__filename}.json")
            
            # checking if a number needs to be appended to the end 
            counter = 0; duped = False
            while os.path.exists(filepath):
                duped = True
                counter += 1
                filepath = os.path.join(SAVED_FOLDER, f"{self.__filename}_{counter}.json")
            if duped: self.__filename = f"{self.__filename}_{counter}"
            
            # put it in the index
            index = []
            if os.path.exists(SAVED_INDEX_PATH):
                with open(SAVED_INDEX_PATH) as f:
                    index = json.load(f)
            index.append({
                "filename": self.__filename,
                "title": self.__title,
                "grid_size": self.get_grid_size(),
                "created_date": self.__created_date
            })
            with open(SAVED_INDEX_PATH, "w") as f:
                json.dump(index, f, indent=4)
                
        # just find the existing file
        else:
            filepath = os.path.join(SAVED_FOLDER, f"{self.__filename}.json")
                
        # save crossword to file
        data = {
            "title": self.__title,
            "created_date": self.__created_date,
            "filename": self.__filename,
            "grid_size": self.__GRID_SIZE,
            "clue_sentences": self.__clue_sentences_to_dict(),
            "grid": self.__grid,
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    
    @classmethod
    def load(cls, filename):
        """
        Deserialises a crossword from a JSON file and returns a new Crossword instance.
        
        Args:
            filename (str): The name of the file to load from.
        
        Returns:
            Crossword: A new Crossword instance populated with the saved data.
        """
        filepath = os.path.join(SAVED_FOLDER, f"{filename}.json")
        with open(filepath, "r") as f:
            data = json.load(f)
        crossword = cls(data["grid_size"], data["title"], data["created_date"], data["filename"])
        crossword.set_grid(data["grid"])
        crossword.__update_clues(data["clue_sentences"])
        return crossword

    def __clue_sentences_to_dict(self):
        """Returns a dictionary containing all the clue sentences, with the corresponding clue number."""
        sentences_dict = {'A': {}, 'D': {}}
        for clue in self.__all_clues:
            sentences_dict[clue.direction][clue.clue_number] = clue.clue_sentence
        return sentences_dict

    # layout related methods
    def __update_numbered_cells(self):
        self.__numbered_cells = []
        self.__checked_cells = set()
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
            
            if self.is_cell_checked((row, col)): self.__checked_cells.add((row, col))
            
    def __update_clues(self, sentences=None): 
        # done after layout is confirmed, and always updates numbered cells
        # all_clues is ordered by accross asc, then down asc
        self.__update_numbered_cells()
        
        self.__all_clues = []
        across = []
        down = []
        
        for index, (cell_row, cell_col, direction) in enumerate(self.__numbered_cells):
            clue_number = index+1 # the actual clue number is +1 because indices start at 0
            
            for d in direction:
                current_row, current_col = cell_row, cell_col
                if d == 'A': d_row, d_col = 0, 1
                if d == 'D': d_row, d_col = 1, 0
                length = 0
                word = ""
                while current_row <= self.__GRID_SIZE-1 and current_col <= self.__GRID_SIZE-1:
                    if self.__grid[current_row][current_col] == BLOCKED_CELL: break
                    length += 1
                    word += self.__grid[current_row][current_col]
                    current_row += d_row
                    current_col += d_col
                
                # find sentence if exists
                clue_sentence = ""
                if sentences:
                    if str(clue_number) in sentences[d].keys():
                        clue_sentence = sentences[d][str(clue_number)]
                    
                new_clue = CW_Clue(self, cell_row, cell_col, d, length, clue_number, word, clue_sentence)
                if d == 'A': across.append(new_clue)
                if d == 'D': down.append(new_clue)
                
        self.__all_clues = across + down
        
        for clue in self.__all_clues:
            clue.intersection_positions = [i for i, cell in enumerate(clue.cells) if cell in self.__checked_cells]

    def flip_blocked_symmetry(self, row, col, symmetry):
        """
        Flip the cell at (row, col) between blocked and empty, applying the given symmetry so that corresponding cells are also fliped to match.

        Args:
            row (int): Row index of the cell to flip.
            col (int): Column index of the cell to flip.
            symmetry (int): Symmetry mode. 1 for no symmetry, 2 for 2-fold, 4 for 4-fold.
        """
        self.__flip_blocked(row, col)
        target = self.__grid[row][col]
        
        other_cells = set()
        if symmetry == 2:
            other_cells.add((self.__GRID_SIZE-1-row, self.__GRID_SIZE-1-col))
            
        if symmetry == 4:
            other_cells.add((self.__GRID_SIZE-1-row, self.__GRID_SIZE-1-col))
            other_cells.add((col, self.__GRID_SIZE-1-row))
            other_cells.add((self.__GRID_SIZE-1-col, row))
            
        for cell_row, cell_col in other_cells:
            self.__flip_blocked(cell_row, cell_col, target)
        
        self.__update_clues()
        
    def __flip_blocked(self, row, col, target=None): 
        """Flip between blocked and empty for one cell. If target is given, then the cell is set to the target instead."""
        if target == None:
            if self.__grid[row][col] == EMPTY_CELL: target = BLOCKED_CELL
            elif self.__grid[row][col] == BLOCKED_CELL: target = EMPTY_CELL
        self.__grid[row][col] = target

    def clues_containing_cell(self, row, col):
        """
        Returns all clues that pass through the given cell.

        Args:
            row (int): Row # of the cell.
            col (int): Column # of the cell.

        Returns:
            set[CW_Clue]: Set of clues that contain the cell.
        """
        clues = set()
        for clue in self.__all_clues:
            if (row, col) in clue.cells: clues.add(clue)
        return clues

    # editing words
    def change_letter(self, row, col, letter, update_lengths=True):
        """
        Updates the letter at the given cell in the grid and in all clues containing that cell.

        Args:
            row (int): Row # of the cell.
            col (int): Column # of the cell.
            letter (chr): The new letter to place in the cell.
            update_lengths (bool): Whether to update word lengths in affected clues. Defaults to True.
        """
        self.__grid[row][col] = letter
        for clue in self.clues_containing_cell(row, col):
            clue.change_letter(row, col, letter, update_lengths)

    # general getters and setters and checks
    def get_grid_size(self):
        """
        Returns the size of the grid.

        Returns:
            int: The number of rows/columns in the grid.
        """
        return self.__GRID_SIZE
    
    def get_grid(self):
        """
        Returns the 2D grid list.

        Returns:
            list[list[str]]: The grid, where each cell contains a letter, EMPTY_CELL, or BLOCKED_CELL.
        """
        return self.__grid
    
    def get_all_clues(self):
        """
        Returns all clues in the crossword, ordered by across ascending then down ascending.

        Returns:
            list[CW_Clue]: List of all clues.
        """
        return self.__all_clues
    
    def set_grid(self, grid, sentences=None):
        """
        Replaces the current grid with the given one and updates all clue sentences.

        Args:
            grid (list[list[str]]): The new grid to set.
            sentences (dict): Clue sentences to restore, if given.
        """
        if len(grid) != self.__GRID_SIZE: raise Exception("something's wrong")
        self.__grid = grid
        self.__update_clues(sentences)
    
    def get_letter_in_cell(self, row, col):
        """
        Returns the character stored at the given cell.

        Args:
            row (int): Row # of the cell.
            col (int): Column # of the cell.

        Returns:
            str: The character at the cell (letter, EMPTY_CELL, or BLOCKED_CELL).
        """
        return self.__grid[row][col]

    def get_numbered_cells(self):
        """
        Returns the list of numbered cells in the grid.

        Returns:
            list[tuple[int, int, str]]: List of (row, col, direction) tuples for each numbered cell.
        """
        return self.__numbered_cells

    def get_blocked_cells_count(self):
        """
        Returns the total number of blocked cells in the grid.

        Returns:
            int: The count of blocked cells.
        """
        return sum(cell == BLOCKED_CELL for row in self.__grid for cell in row)

    def get_checked_cells_count(self):
        """
        Returns the number of cells that belong to both an across and a down word.

        Returns:
            int: The count of checked cells.
        """
        return sum([self.is_cell_checked((row, col)) for row in range(self.__GRID_SIZE) for col in range(self.__GRID_SIZE)])

    def get_all_word_lengths(self):
        """
        Returns a dictionary mapping word lengths to how many words of that length exist in the grid.

        Returns:
            dict[int, int]: A dictionary where keys are word lengths and values are counts.
        """
        word_lengths = {}
        for clue in self.__all_clues:
            if clue.length not in word_lengths.keys():
                word_lengths[clue.length] = 1
            else:
                word_lengths[clue.length] += 1
        return word_lengths

    def empty_grid(self):
        """Resets all cells in the grid to EMPTY_CELL."""
        self.__grid = [[EMPTY_CELL]*self.__GRID_SIZE for _ in range(self.__GRID_SIZE)]
        self.__update_clues()
        
    def clear_grid(self):
        """Removes all letters from the grid while preserving blocked cells."""
        newGrid = [[EMPTY_CELL if cell != BLOCKED_CELL else BLOCKED_CELL for cell in row] for row in self.__grid]
        self.__grid = deepcopy(newGrid)
        self.__update_clues()
    
    def is_grid_empty(self):
        """
        Checks whether all cells in the grid are empty.

        Returns:
            bool: True if every cell is EMPTY_CELL, False otherwise.
        """
        for row in self.__grid:
            for cell in row:
                if cell != EMPTY_CELL: return False
        return True
    
    def is_grid_clear(self):
        """
        Checks whether the grid contains no letters.

        Returns:
            bool: True if every cell is either EMPTY_CELL or BLOCKED_CELL, False otherwise.
        """
        for row in self.__grid:
            for cell in row:
                if not(cell == EMPTY_CELL or cell == BLOCKED_CELL): return False
        return True

    def is_cell_checked(self, cell):
        """
        Checks whether a cell belongs to both an across and a down word.

        Args:
            cell (tuple[int, int]): The (row, col) position of the cell.

        Returns:
            bool: True if the cell is part of both an across and a down word.
        """
        return self.is_cell_in_word(cell, 'A') and self.is_cell_in_word(cell, 'D')

    def is_cell_in_word(self, cell, dir):
        """
        Checks whether a cell is part of a word in the given direction.

        Args:
            cell (tuple[int, int]): The (row, col) position of the cell.
            dir (str): The direction to check. 'A' for across, 'D' for down.

        Returns:
            bool: True if the cell is part of a word in the given direction.
        """
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

    def to_cell_number(self, r, c):
        """
        Converts a (row, col) grid position to a unique integer cell number.

        Args:
            r (int): Row #.
            c (int): Column #.

        Returns:
            int: The cell number corresponding to the given position.
        """
        return r * self.__GRID_SIZE + c

    def print_grid(self):
        """Prints a text representation of the grid to the console. Used for debugging"""
        print('\n'.join(['|'.join([' ' if not c else c for c in row]) for row in self.__grid]))    
        