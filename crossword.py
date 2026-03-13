# cw_model.py

from app_settings import *
from copy import deepcopy
from itertools import product
from datetime import date
import os
import json

from cw_clue import CW_Clue

class Crossword:
    def __init__(self, grid_size, title, created_date=str(date.today()), filename=""):
        """
        selected_cell: (int, int)
        selected_direction: "A" / "D"
        """
        
        ## META DATA
        self.__title = title
        self.__created_date = created_date
        self.__filename = filename
        
        self.__GRID_SIZE = grid_size
        self.__grid = [] # coordinates are 0-indexed
        self.empty_grid()

        self.__numbered_cells = [] # (row, col, direction)
        self.__update_clues()
        self.__all_clues = []

    # saving / loading
    def save(self):
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
        filepath = os.path.join(SAVED_FOLDER, f"{filename}.json")
        with open(filepath, "r") as f:
            data = json.load(f)
        crossword = cls(data["grid_size"], data["title"], data["created_date"], data["filename"])
        crossword.set_grid(data["grid"])
        return crossword

    def __clue_sentences_to_dict(self):
        sentences_dict = {'A': {}, 'D':{}}
        for clue in self.__all_clues:
            sentences_dict[clue.direction][clue.clue_number] = clue.clue_sentence
        return sentences_dict

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
            
    def __update_clues(self, sentences=None): # done after layout is confirmed, and always updates numbered cells
        self.__update_numbered_cells()
        
        self.__all_clues = []
        for index, (cell_row, cell_col, direction) in enumerate(self.__numbered_cells):
            clue_number = index+1 # the actual clue number is +1 becase indices start at 0
            
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
                    if clue_number in sentences[d].keys():
                        clue_sentence = sentences[d][clue_number]
                    
                new_clue = CW_Clue(self, cell_row, cell_col, d, length, clue_number, word, clue_sentence)
                self.__all_clues.append(new_clue)

    def flip_blocked_symmetry(self, row, col, symmetry):
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
        
    def __flip_blocked(self, row, col, target=None): # flip for one cell
        if target == None:
            if self.__grid[row][col] == EMPTY_CELL: target = BLOCKED_CELL
            elif self.__grid[row][col] == BLOCKED_CELL: target = EMPTY_CELL
        self.__grid[row][col] = target

    def clues_containing_cell(self, row, col):
        clues = set()
        for clue in self.__all_clues:
            if (row, col) in clue.cells: clues.add(clue)
        return clues

    # editing words
    def change_letter(self, row, col, letter):
        self.__grid[row][col] = letter
        for clue in self.clues_containing_cell(row, col):
            clue.change_letter(row, col, letter)

    # general getters and setters and checks
    def get_grid_size(self):
        return self.__GRID_SIZE
    
    def get_grid(self):
        return self.__grid
    
    def get_all_clues(self):
        return self.__all_clues
    
    def set_grid(self, grid, sentences=None):
        if len(grid) != self.__GRID_SIZE: raise Exception("something's wrong")
        self.__grid = grid
        self.__update_clues(sentences)
    
    def get_letter_in_cell(self, row, col):
        return self.__grid[row][col]

    def get_numbered_cells(self):
        return self.__numbered_cells

    def empty_grid(self):
        self.__grid = [[EMPTY_CELL]*self.__GRID_SIZE for _ in range(self.__GRID_SIZE)]
        self.__update_clues()
        
    def clear_grid(self):
        newGrid = [[EMPTY_CELL if cell != BLOCKED_CELL else BLOCKED_CELL for cell in row] for row in self.__grid]
        self.__grid = deepcopy(newGrid)
        self.__update_clues()
    
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

    def print_grid(self):
        print('\n'.join(['|'.join([' ' if not c else c for c in row]) for row in self.__grid]))
        
        