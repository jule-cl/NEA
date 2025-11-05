# crossword_filler.py

"""
apparently this is better
searches through clues and backtracks when fails

algorithm outline:
order clues to fill by "priority"
get most "prioritised" clue
if no possible words fit in that space:
    get rid of the most recent clue placed that intersects with the clue and try again
if there are words:
    pick word (pattern) and place it there

TODO:
the process of choosing a candidate can be reworked to get better words
"""

from random import choice

from word_funcs import get_word_score
from cw_clue import CW_Clue
from pqueue import PQueue
from app_settings import *
      
class Auto_Fill:
    def __init__(self, grid):
        self.grid = grid
        self.__GRID_SIZE = len(grid)
        
        self.__all_clues = []
        self.__corner_clues = {}
        self.__corner_checked = {}
        self.__update_clues_and_corners()
        
    def __update_clues_and_corners(self):
        self.__all_clues = []
        cell_clue_directions = [[[] for _ in range(self.__GRID_SIZE)] for __ in range(self.__GRID_SIZE)]
        
        for row in range(len(self.grid)):
            for col in range(len(self.grid)):
                
                '''
                CLUES CHECK
                '''
                # blocked
                if self.grid[row][col] == BLOCKED_CELL: continue
                
                # across
                if col >= self.__GRID_SIZE-2: pass
                elif self.grid[row][col-1] == BLOCKED_CELL or col == 0: 
                    # find length of word
                    word_length = 1
                    t_col = col + 1
                    while t_col <= len(self.grid)-1:
                        if self.grid[row][t_col] == BLOCKED_CELL: break
                        word_length += 1
                        t_col += 1
                        
                    if word_length >= 3:
                        new_clue = CW_Clue(row, col, 'A', word_length, [(row, col+i) for i in range(word_length)], self)
                        self.__all_clues.append(new_clue)
                        for i in range(word_length):
                            cell_clue_directions[row][col+i].append(new_clue)
                        
                # down
                if row >= self.__GRID_SIZE-2: pass
                elif self.grid[row-1][col] == BLOCKED_CELL or row == 0: 
                    # find length of word
                    word_length = 1
                    t_row = row + 1
                    while t_row <= len(self.grid)-1:
                        if self.grid[t_row][col] == BLOCKED_CELL: break
                        word_length += 1
                        t_row += 1
                        
                    if word_length >= 3:
                        new_clue = CW_Clue(row, col, 'D', word_length, [(row+i, col) for i in range(word_length)], self)
                        self.__all_clues.append(new_clue)
                        for i in range(word_length):
                            cell_clue_directions[row+i][col].append(new_clue)

        # find corner positions, the clues that go through them, and initialise whether they have been filled from either direction
        for index_r, row in enumerate(cell_clue_directions):
            for index_c, col in enumerate(row):
                if len(col) == 2: # both part of across and down
                    self.__corner_clues[self.__to_cell_number(index_r, index_c)] = (col[0], col[1])
                    self.__corner_checked[self.__to_cell_number(index_r, index_c)] = {'A':False, 'D':False}
        
        # find which clues intersect which clues
        for clue in self.__all_clues:
            clue.intersections = []
            for row, col in clue.cells:
                cell_num = self.__to_cell_number(row, col)
                if cell_num in self.__corner_clues.keys():
                    clue1, clue2 = self.__corner_clues[cell_num]
                    clue.intersections.append(clue1)
                    clue.intersections.append(clue2)
                    
            # get positions of intersection
            clue.intersection_positions = [i for i, cell in enumerate(clue.cells) if self.__to_cell_number(cell[0], cell[1]) in self.__corner_checked.keys()]
                        
    def fill(self, constraint=10):
        self.used_words = set()
        self.filled_clues = []
        
        self.ordered_clues = PQueue()
        for clue in self.__all_clues:
            clue.update_score()
            self.ordered_clues.insert_node(clue)

        # main search
        while self.ordered_clues.get_root():

            if self.ordered_clues.get_root().score == 0 or self.ordered_clues.get_root().attempts == constraint: # no possibilities, so backtrack 
                if not self.filled_clues: return False # back to first clue, no solutions
                self.__remove_clue(self.__find_conflict_source(self.ordered_clues.get_root()))
                    
                continue 
            
            self.current_clue = self.ordered_clues.pop_index(0)
                  
            candidates = self.current_clue.get_possible_words()
            # choose a word
            selected_word = candidates[0]
        
            # attempt to place pattern
            self.__place_word(self.current_clue, selected_word)
            self.filled_clues.append(self.current_clue)
            self.used_words.add(selected_word)
            self.__update_priority()
            self.current_clue.attempts += 1
                
            # print(len(self.filled_clues), len(self.ordered_clues.queue))
            # self.print_grid()

        return True
    
    def __find_conflict_source(self, failed_clue):
        for clue in self.filled_clues[::-1]:
            if set(clue.cells).union(set(failed_clue.cells)): return clue
            
    def __remove_clue(self, clue_to_remove):
        # remove word from grid and allow pattern to be used again
        removed_word = self.__remove_word(clue_to_remove)
        self.used_words.remove(removed_word)
        # record the failed pattern, not letting to be used in this clue
        clue_to_remove.failed_words.append(removed_word)
        
        # reset attempts for intersecting clues
        for clue in clue_to_remove.intersections:
            if self.ordered_clues.has_node(clue):
                clue.attempts = 0
                # clue.failed_words = []
        
        # put clue back in and update priority
        self.filled_clues.remove(clue_to_remove)
        self.ordered_clues.insert_node(clue_to_remove)
        self.__update_priority()
    
    def __place_word(self, clue, word):
        for index, (row, col) in enumerate(clue.cells):
            if self.grid[row][col] not in [word[index], EMPTY_CELL]: raise Exception("something already there")
                
            # place it 
            self.grid[row][col] = word[index]
            
            # check if the cell is checked
            cell_num = self.__to_cell_number(row, col)
            if cell_num in self.__corner_checked.keys():
                self.__corner_checked[cell_num][clue.direction] = True
            
    def __remove_word(self, clue):
        word = ""
        for row, col in clue.cells:
            if self.grid[row][col] == EMPTY_CELL: raise Exception("clue not filled")
            word += self.grid[row][col]
            
            cell_num = self.__to_cell_number(row, col)
            other_dir = 'A' if clue.direction == 'D' else 'D'
            
            if cell_num in self.__corner_checked.keys():
                self.__corner_checked[cell_num][clue.direction] = False
                if self.__corner_checked[cell_num][other_dir]: continue # if the cell was filled from the other direction
            self.grid[row][col] = EMPTY_CELL
            

            
        return word
                
    def __update_priority(self):
        for clue in self.__all_clues:
            clue.update_score()
            if self.ordered_clues.has_node(clue): 
                self.ordered_clues.pop_node(clue)
                self.ordered_clues.insert_node(clue)
                
    def __to_cell_number(self, r, c):
        return r * self.__GRID_SIZE + c

    def print_grid(self):
        print('\n'.join([' '.join([c if c else '?' for c in row]) for row in grid])+'\n')

if __name__ == '__main__':
    import time
    from cw_layout_filler import Crossword_Layout
    
    layout = Crossword_Layout(size=11)
    
    start = time.time()
    grid = layout.generate_layout(seed=3)
    end = time.time()
    print(f'layout gen: {end-start:.2f} s')
    
    filler = Auto_Fill(grid)
    filler.print_grid()
    
    start = time.time()
    filler.fill(constraint=5)
    end = time.time()
    
    filler.print_grid()
    print(f'Auto fill: {end-start:.2f} s')

