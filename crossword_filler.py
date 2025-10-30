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

from copy import deepcopy
from random import choice
from word_funcs import get_words_that_match, get_word_score
from math import inf
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
                        new_clue = Clue(row, col, 'A', word_length, [(row, col+i) for i in range(word_length)], self)
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
                        new_clue = Clue(row, col, 'D', word_length, [(row+i, col) for i in range(word_length)], self)
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
        self.used_patterns = set()
        self.filled_clues = []
        
        self.ordered_clues = PQueue()
        for clue in self.__all_clues:
            clue.update_score()
            self.ordered_clues.insert_node(clue)

        # main search
        while self.ordered_clues.get_root():

            if self.ordered_clues.get_root().score == 0: # no possibilities, so backtrack 
                if not self.filled_clues: return False # back to first clue, no solutions
                self.__remove_clue(self.__find_conflict_source(self.ordered_clues.get_root()))
                    
                continue 
            
            self.current_clue = self.ordered_clues.pop_index(0)
                  
            candidates = self.current_clue.get_possible_patterns()
            candidates = sorted(candidates, key=lambda x: get_word_score(x), reverse=True)[:constraint]
            # choose a pattern
            selected_pattern = choice(candidates)
        
            # attempt to place pattern
            self.__place_pattern(self.current_clue, selected_pattern)
            self.filled_clues.append(self.current_clue)
            self.used_patterns.add(selected_pattern)
            self.__update_priority()
                
            print(len(self.filled_clues), len(self.ordered_clues.queue))
            self.print_grid()

        for clue in self.__all_clues:
            candidates = clue.get_possible_words()
            self.__place_word(clue, choice(candidates))
        return True
    
    def __find_conflict_source(self, failed_clue):
        for clue in self.filled_clues[::-1]:
            if set(clue.cells).union(set(failed_clue.cells)): return clue
            
    def __remove_clue(self, clue_to_remove):
        # remove word from grid and allow pattern to be used again
        removed_pattern = self.__remove_pattern(clue_to_remove)
        self.used_patterns.remove(removed_pattern)
        # record the failed pattern, not letting to be used in this clue
        clue_to_remove.failed_patterns.append(removed_pattern)
        
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
            
    def __place_pattern(self, clue, pattern):
        for index, pos in enumerate(clue.intersection_positions):
            row, col = clue.cells[pos]
            # place it 
            self.grid[row][col] = pattern[index]
            
            cell_num = self.__to_cell_number(row, col)
            self.__corner_checked[cell_num][clue.direction] = True
               
    def __remove_pattern(self, clue):
        pattern = ""
        for row, col in clue.cells:
            if self.grid[row][col] == EMPTY_CELL: continue
            pattern += self.grid[row][col]
            
            cell_num = self.__to_cell_number(row, col)
            other_dir = 'A' if clue.direction == 'D' else 'D'
            
            if cell_num in self.__corner_checked.keys():
                self.__corner_checked[cell_num][clue.direction] = False
                if self.__corner_checked[cell_num][other_dir]: continue # if the cell was filled from the other direction
            self.grid[row][col] = EMPTY_CELL
            

            
        return pattern
                
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

# min heap (to get priority)
class PQueue:
    def __init__(self):
        self.queue = []
    
    def __get_children_indicies(self, i):
        left = i*2+1
        if left >= len(self.queue): left = None
        right = i*2+2
        if right >= len(self.queue): right = None
        return (left, right)
    
    def __get_parent_index(self, i):
        return (i-1)//2
    
    def __get_node_at_index(self, i):
        return self.queue[i] if i else None
    
    def get_root(self):
        if len(self.queue) == 0: return None
        return self.queue[0]
    
    def pop_node(self, node):
        current_index = self.queue.index(node)
        
        # if thing to pop is already at the end
        if current_index == len(self.queue)-1:
            return self.queue.pop()
        
        self.queue[current_index] = self.queue.pop()
        
        while True:
            index_l, index_r = self.__get_children_indicies(current_index)
            left, right = self.__get_node_at_index(index_l), self.__get_node_at_index(index_r)
            
            if left and left.score < self.queue[current_index].score:
                self.queue[current_index], self.queue[index_l] = self.queue[index_l], self.queue[current_index]
                current_index = index_l
                continue
                
            if right and right.score < self.queue[current_index].score:
                self.queue[current_index], self.queue[index_r] = self.queue[index_r], self.queue[current_index]
                current_index = index_r
                continue
            
            break
        return node

    def pop_index(self, index):
        if index >= len(self.queue): return None
        return self.pop_node(self.queue[index])

    def insert_node(self, node):
        self.queue.append(node)
        
        current_index = len(self.queue)-1
        while True:
            index_p = self.__get_parent_index(current_index)
            parent = self.__get_node_at_index(index_p)
            
            if parent and parent.score > self.queue[current_index].score:
                self.queue[current_index], self.queue[index_p] = self.queue[index_p], self.queue[current_index]
                current_index = index_p
                continue
            
            break

    def has_node(self, node):
        return node in self.queue

class Clue:
    def __init__(self, row, col, direction, length, cells, parent_grid):
        self.row = row
        self.col = col
        self.direction = direction
        self.length = length 
        self.parent_grid = parent_grid
        
        self.cells = cells
        self.intersections = []
        self.intersection_positions = []
        
        self.failed_patterns = []
        
        self.score = inf
        
    def __get_regex(self):
        return ''.join(['*' if (c:=self.parent_grid.grid[row][col])==EMPTY_CELL else c for (row, col) in self.cells])
    
    def get_possible_words(self):
        regex = self.__get_regex()
        return sorted([w.upper() for w in get_words_that_match(regex)], key=lambda w:get_word_score(w), reverse=True)
    
    def get_possible_patterns(self):
        # find all possible patterns
        candidates = list(set([''.join([checked[i] for i in self.intersection_positions]) for checked in self.get_possible_words()]))
        # filter out used patterns and ones that fail
        candidates = list(filter(lambda p: p not in self.parent_grid.used_patterns and p not in self.failed_patterns, candidates))
        return candidates
    
    # based off patterns rather than words
    def update_score(self):
        self.score = len(self.get_possible_patterns())
        
if __name__ == '__main__':
    import time
    from crossword_layout import Crossword_Layout
    
    layout = Crossword_Layout(size=9)
    
    start = time.time()
    grid = layout.generate_layout(seed=3)
    end = time.time()
    print(f'layout gen: {end-start:.2f} s')
    
    filler = Auto_Fill(grid)
    
    start = time.time()
    print(filler.fill(constraint=5))
    end = time.time()
    
    filler.print_grid()
    print(f'Auto fill: {end-start:.2f} s')

