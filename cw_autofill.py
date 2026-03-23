# cw_autofill.py

"""
algorithm outline:
order clues to fill by "priority"
get most "prioritised" clue
if no possible words fit in that space:
    get rid of the most recent clue placed that intersects with the clue and try again
if there are words:
    pick word (pattern) and place it there
"""

from copy import deepcopy

from cw_clue import CW_Clue
from minheap import Min_Heap
from app_info import *

class Autofill:
    """
    Automatically fills a crossword grid with valid words using a backtracking search algorithm.
    Clues are prioritised by a score reflecting how constrained they are.
    The algorithm backtracks when no valid word can be placed in a slot, or the maximum attempts have been reached.

    Variables:
        __crossword (Crossword): A deep copy of the crossword object being filled.
        __GRID_SIZE (int): The size of the grid.
        __all_clues (list[CW_Clue]): List of all clue objects in the crossword.
        __corner_clues (dict): Maps cell numbers to their across and down clues for intersecting cells.
        __corner_checked (dict): Maps cell numbers to whether each direction has been filled.

    Methods:
        fill: Runs the autofill algorithm and returns the completed crossword or False if unsolvable.
    """
    def __init__(self, crossword):
        """
        Initialises the Autofill instance with a deep copy of the given crossword.

        Args:
            crossword (Crossword): The crossword object to autofill.
        """
        self.__crossword = deepcopy(crossword)
        self.__GRID_SIZE = self.__crossword.get_grid_size()
        
        self.__all_clues = self.__crossword.get_all_clues()
        self.__corner_clues = {}
        self.__corner_checked = {}
        self.__update_corners()
        
    def __update_corners(self):
        """
        Finds all cells part of two words (corners) in the grid and records which clues pass through them in each direction.
        """
        cell_clue_directions = [[{} for _ in range(self.__GRID_SIZE)] for __ in range(self.__GRID_SIZE)]
        for clue in self.__all_clues:
            for cell_row, cell_col in clue.cells:
                cell_clue_directions[cell_row][cell_col][clue.direction] = clue

        for index_r, row in enumerate(cell_clue_directions):
            for index_c, col in enumerate(row):
                if len(col.keys()) == 2:
                    self.__corner_clues[self.__to_cell_number(index_r, index_c)] = {'A':col['A'], 'D':col['D']}
                    self.__corner_checked[self.__to_cell_number(index_r, index_c)] = {'A':False, 'D':False}
        
        for clue in self.__all_clues:
            clue.intersections = set()
            for row, col in clue.cells:
                cell_num = self.__to_cell_number(row, col)
                if cell_num in self.__corner_clues.keys(): 
                    for intersecting_clue in self.__corner_clues[cell_num].values():
                        if intersecting_clue != clue: clue.intersections.add(intersecting_clue)
                    
            # get positions of intersection
            clue.intersection_positions = [i for i, cell in enumerate(clue.cells) if self.__to_cell_number(cell[0], cell[1]) in self.__corner_checked.keys()]
                        
    def fill(self, constraint=5):
        """
        Runs the backtracking autofill algorithm, placing words into clue slots in priority order.
        Backtracks when a slot has no valid candidates or has exceeded the attempt limit.

        Args:
            constraint (int): The maximum number of attempts allowed per clue before the algorithm backtracks. Defaults to 5.

        Returns:
            Crossword: The filled crossword object if a solution is found.
            bool: False if no solution exists.
        """
        self.filled_clues = []
        
        self.clues_to_fill = Min_Heap()
        for clue in self.__all_clues:
            clue.update_score()
            self.clues_to_fill.insert_node(clue)

        # main search
        while self.clues_to_fill.get_root():

            self.current_clue = self.clues_to_fill.get_root()

            if not self.current_clue.get_possible_words() or self.current_clue.attempts == constraint: # no possibilities, so backtrack 
                if not self.filled_clues: return False # back to first clue, no solutions
                self.__remove_clue(self.__find_conflict_source(self.clues_to_fill.get_root()))
                continue 
            
            self.current_clue = self.clues_to_fill.pop_index(0)
                  
            # pick the "best" word
            candidates = self.current_clue.get_possible_words()
            selected_word = candidates[0]
        
            # place word in grid
            self.__place_word(self.current_clue, selected_word)
            self.filled_clues.append(self.current_clue)
            self.__update_priority(self.current_clue)
            self.current_clue.attempts += 1

        return self.__crossword
    
    def __find_conflict_source(self, failed_clue):
        """
        Finds the most recently filled clue that intersects with the given failed clue.

        Args:
            failed_clue (CW_Clue): The clue that could not be filled.

        Returns:
            CW_Clue: The most recently filled intersecting clue, or the last filled clue if no intersection is found.
        """
        for clue in self.filled_clues[::-1]:
            if set(clue.cells).intersection(set(failed_clue.cells)): return clue
            
        # if no intersection found, return most recent
        return self.filled_clues[-1] if self.filled_clues else None
            
    def __remove_clue(self, clue_to_remove):
        """
        Removes the word in the given clue slot from the grid, and records it as a failed word for that clue.
        
        Args:
            clue_to_remove (CW_Clue): The clue whose word should be removed and retried.
        """
        removed_word = self.__remove_word(clue_to_remove)
        self.__remove_from_used_words(removed_word)
        # record the failed pattern, not letting to be used in this clue
        clue_to_remove.failed_words.add(removed_word)
        
        # reset attempts for intersecting clues
        for clue in clue_to_remove.intersections:
            if self.clues_to_fill.has_node(clue):
                clue.attempts = 0
            
        # put clue back in and update priority
        self.filled_clues.remove(clue_to_remove)
        self.clues_to_fill.insert_node(clue_to_remove)
        self.__update_priority(clue_to_remove)
    
    def __place_word(self, clue, word):
        """
        Places a word into the grid at the given clue slot.
        Updates scores of clues intersecting the filled clue.

        Args:
            clue (CW_Clue): The clue slot to fill.
            word (str): The word to place in the grid.
        """
        self.__add_to_used_words(word)
        for index, (row, col) in enumerate(clue.cells):
            self.__crossword.change_letter(row, col, word[index])
            
            # set checked to true in the correct direction and place it in the other
            cell_num = self.__to_cell_number(row, col)
            if cell_num in self.__corner_checked.keys():
                self.__corner_checked[cell_num][clue.direction] = True
            
    def __remove_word(self, clue):
        """
        Removes a word from the grid for the given clue.
        Clears cell that are not still filled by an intersecting clue in the other direction.

        Args:
            clue (CW_Clue): The clue whose word should be removed.

        Returns:
            str: The word that was removed.
        """
        word = clue.word
        for row, col in clue.cells:
            cell_num = self.__to_cell_number(row, col)
            other_dir = CW_Clue.other_direction(clue.direction)
            
            if cell_num in self.__corner_checked.keys():
                self.__corner_checked[cell_num][clue.direction] = False
                if self.__corner_checked[cell_num][other_dir]: continue # if the cell was filled from the other direction

            # clear letter from original clue
            self.__crossword.change_letter(row, col, EMPTY_CELL)
            
        return word
        
    def __add_to_used_words(self, word):
        """
        Marks a word as used across all clues, preventing it from being placed again.

        Args:
            word (str): The word to mark as used.
        """
        for clue in self.__all_clues:
            clue.used_words.add(word)
            
    def __remove_from_used_words(self, word):
        """
        Removes a word from the used words set across all clues, allowing it to be placed again.

        Args:
            word (str): The word to unmark as used.
        """
        for clue in self.__all_clues:
            clue.used_words.remove(word)
          
    def __update_priority(self, affected_clue):
        """
        Updates the priority score of the affected clue and all clues that intersect it, reinserting them into the priority queue with their new scores.

        Args:
            affected_clue (CW_Clue): The clue whose placement has affected intersecting clues.
        """
        for clue in affected_clue.intersections.union(set([affected_clue])):
            if self.clues_to_fill.has_node(clue): 
                self.clues_to_fill.pop_node(clue)
                clue.update_score()
                self.clues_to_fill.insert_node(clue)
                
    def __to_cell_number(self, r, c):
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
        """
        Used for debugging.
        Prints a text representation of the current grid state to the console, displaying '?' for empty cells.
        """
        print('\n'.join([' '.join([c if c else '?' for c in row]) for row in self.grid])+'\n')
