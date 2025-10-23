# crossword_filler.py

from copy import deepcopy
from random import choice, shuffle
from word_funcs import get_words_that_match, get_word_score
from math import inf
from app_settings import *
      
class Auto_Fill:
    def __init__(self, grid):
        self.__grid = grid
        self.__GRID_SIZE = len(grid)
        
        self.__clues = []
        self.__corner_clues = {}
        self.__corner_checked = {}
        self.__update_clues_and_corners()
        
    def __update_clues_and_corners(self):
        self.__clues = []
        cell_clue_directions = [[[] for _ in range(self.__GRID_SIZE)] for __ in range(self.__GRID_SIZE)]
        
        for row in range(len(self.__grid)):
            for col in range(len(self.__grid)):
                
                '''
                CLUES CHECK
                '''
                # blocked
                if self.__grid[row][col] == BLOCKED_CELL: continue
                
                # across
                if col >= self.__GRID_SIZE-2: pass
                elif self.__grid[row][col-1] == BLOCKED_CELL or col == 0: 
                    # find length of word
                    word_length = 1
                    t_col = col + 1
                    while t_col <= len(self.__grid)-1:
                        if self.__grid[row][t_col] == BLOCKED_CELL: break
                        word_length += 1
                        t_col += 1
                        
                    if word_length >= 3:
                        new_clue = Clue(row, col, 'A', word_length, [(row, col+i) for i in range(word_length)])
                        self.__clues.append(new_clue)
                        for i in range(word_length):
                            cell_clue_directions[row][col+i].append(new_clue)
                        
                # down
                if row >= self.__GRID_SIZE-2: pass
                elif self.__grid[row-1][col] == BLOCKED_CELL or row == 0: 
                    # find length of word
                    word_length = 1
                    t_row = row + 1
                    while t_row <= len(self.__grid)-1:
                        if self.__grid[t_row][col] == BLOCKED_CELL: break
                        word_length += 1
                        t_row += 1
                        
                    if word_length >= 3:
                        new_clue = Clue(row, col, 'D', word_length, [(row+i, col) for i in range(word_length)])
                        self.__clues.append(new_clue)
                        for i in range(word_length):
                            cell_clue_directions[row+i][col].append(new_clue)

        for index_r, row in enumerate(cell_clue_directions):
            for index_c, col in enumerate(row):
                if len(col) == 2: # both part of across and down
                    self.__corner_clues[self.__to_cell_number(index_r, index_c)] = (col[0], col[1])
                    self.__corner_checked[self.__to_cell_number(index_r, index_c)] = {'A':False, 'D':False}
                        
    def fill(self, constraint=10):
        ordered_clues = PQueue()
        for clue in self.__clues:
            clue.update_score(self.__grid)
            ordered_clues.insert_node(clue)

        # return self.__recur(ordered_clues, set())
        found = self.__recurse(ordered_clues, set(), constraint=constraint)
        if not found: return False
        
        for clue in self.__clues:
            candidates = clue.get_possible(self.__grid)
            self.__place_word(clue, choice(candidates))
        return True
    
    # obselete
    # recursing on clue priority                      
    def __recur(self, ordered_clues, used_words):
        if not ordered_clues.get_root(): return True # done

        current_clue = ordered_clues.pop_index(0)
        candidates = current_clue.get_possible(self.__grid)
        
        for word in candidates:
            # check if word has already been used
            if word in used_words: continue
                    
            # attempt to place word
            self.__place_word(current_clue, word)
            used_words.add(word)
            
            # debugging
            # self.print_grid()
            # print(current_clue.score)
            
            # update priority
            new_priority = deepcopy(ordered_clues)
            for row, col in current_clue.cells:
                cell_num = self.__to_cell_number(row, col)
                if cell_num in self.__corner_clues.keys():
                    clue1, clue2 = self.__corner_clues[cell_num]
                    
                    if new_priority.has_node(clue1):
                        clue1.update_score(self.__grid)
                        new_priority.pop_node(clue1)
                        new_priority.insert_node(clue1)
                    if new_priority.has_node(clue2):
                        clue2.update_score(self.__grid)
                        new_priority.pop_node(clue2)
                        new_priority.insert_node(clue2)
                        
            # if this path leads to good, then just return true
            if self.__recur(new_priority, used_words):
                return True
            
            # need to backtrack
            self.__remove_word(current_clue)
            used_words.remove(word)
                
        return False # solution not found ??      
    
    # recursing on clue priority, but only filling in corners
    def __recurse(self, ordered_clues, used_patterns, constraint=10):
        if not ordered_clues.get_root(): return True # done
        
        current_clue = ordered_clues.pop_index(0)
        positions = [i for i, cell in enumerate(current_clue.cells) if self.__to_cell_number(cell[0], cell[1]) in self.__corner_checked.keys()]
        
        candidates = set([''.join([checked[i] for i in positions]) for checked in current_clue.get_possible(self.__grid)])
        candidates = sorted(list(candidates), key=lambda x: get_word_score(x), reverse=True)
        
        for pattern in candidates[:constraint]:
            # check if pattern has already been used
            # this prevents two words with the same pattern to be used (bat/bet cant both be in a grid where 1 and 3 are checked)
            if pattern in used_patterns: continue
            
            # attempt to place
            self.__place_checked(current_clue, positions, pattern)
            used_patterns.add(pattern)
            
            # update priority
            new_priority = deepcopy(ordered_clues)
            for row, col in current_clue.cells:
                cell_num = self.__to_cell_number(row, col)
                if cell_num in self.__corner_clues.keys():
                    clue1, clue2 = self.__corner_clues[cell_num]
                    
                    if new_priority.has_node(clue1):
                        clue1.update_score(self.__grid)
                        new_priority.pop_node(clue1)
                        new_priority.insert_node(clue1)
                    if new_priority.has_node(clue2):
                        clue2.update_score(self.__grid)
                        new_priority.pop_node(clue2)
                        new_priority.insert_node(clue2)
                        
            # if this path leads to good, then just return true
            if self.__recurse(new_priority, used_patterns):
                return True
            
            # need to backtrack
            self.__remove_word(current_clue)
            used_patterns.remove(pattern)
                
        return False # solution not found ??
    
    def __place_word(self, clue, word):
        for index, (row, col) in enumerate(clue.cells):
            if self.__grid[row][col] not in [word[index], EMPTY_CELL]: raise Exception("something already there")
                
            # place it 
            self.__grid[row][col] = word[index]
            
            # check if the cell is checked
            cell_num = self.__to_cell_number(row, col)
            if cell_num in self.__corner_checked.keys():
                self.__corner_checked[cell_num][clue.direction] = True
            
    def __place_checked(self, clue, positions, checked):
        for index, pos in enumerate(positions):
            row, col = clue.cells[pos]
            # place it 
            self.__grid[row][col] = checked[index]
            
            cell_num = self.__to_cell_number(row, col)
            self.__corner_checked[cell_num][clue.direction] = True
            
    def __remove_word(self, clue):
        for row, col in clue.cells:
            cell_num = self.__to_cell_number(row, col)
            other_dir = 'A' if clue.direction == 'D' else 'D'
            
            if cell_num in self.__corner_checked.keys():
                self.__corner_checked[cell_num][clue.direction] = False
                if self.__corner_checked[cell_num][other_dir]: continue # if the cell was filled from the other direction
            self.__grid[row][col] = EMPTY_CELL
                
    def __to_cell_number(self, r, c):
        return r * self.__GRID_SIZE + c

    def print_grid(self):
        print('\n'.join([' '.join([c if c else '?' for c in row]) for row in grid])+'\n')

# min heap (to get priority)
class PQueue:
    def __init__(self):
        self.__queue = []
    
    def __get_children_indicies(self, i):
        left = i*2+1
        if left >= len(self.__queue): left = None
        right = i*2+2
        if right >= len(self.__queue): right = None
        return (left, right)
    
    def __get_parent_index(self, i):
        return (i-1)//2
    
    def __get_node_at_index(self, i):
        return self.__queue[i] if i else None
    
    def get_root(self):
        if len(self.__queue) == 0: return None
        return self.__queue[0]
    
    def pop_node(self, node):
        current_index = self.__queue.index(node)
        
        # if thing to pop is already at the end
        if current_index == len(self.__queue)-1:
            return self.__queue.pop()
        
        self.__queue[current_index] = self.__queue.pop()
        
        while True:
            index_l, index_r = self.__get_children_indicies(current_index)
            left, right = self.__get_node_at_index(index_l), self.__get_node_at_index(index_r)
            
            if left and left.score < self.__queue[current_index].score:
                self.__queue[current_index], self.__queue[index_l] = self.__queue[index_l], self.__queue[current_index]
                current_index = index_l
                continue
                
            if right and right.score < self.__queue[current_index].score:
                self.__queue[current_index], self.__queue[index_r] = self.__queue[index_r], self.__queue[current_index]
                current_index = index_r
                continue
            
            break
        return node

    def pop_index(self, index):
        if index >= len(self.__queue): return None
        return self.pop_node(self.__queue[index])

    def insert_node(self, node):
        self.__queue.append(node)
        
        current_index = len(self.__queue)-1
        while True:
            index_p = self.__get_parent_index(current_index)
            parent = self.__get_node_at_index(index_p)
            
            if parent and parent.score > self.__queue[current_index].score:
                self.__queue[current_index], self.__queue[index_p] = self.__queue[index_p], self.__queue[current_index]
                current_index = index_p
                continue
            
            break

    def has_node(self, node):
        return node in self.__queue

class Clue:
    def __init__(self, row, col, direction, length, cells):
        self.row = row
        self.col = col
        self.direction = direction
        self.length = length 
        self.cells = cells
        
        self.score = inf
        
    def __get_regex(self, grid):
        return ''.join(['*' if (c:=grid[row][col])==EMPTY_CELL else c for (row, col) in self.cells])
    
    def get_possible(self, grid):
        regex = self.__get_regex(grid)
        return sorted([w.upper() for w in get_words_that_match(regex)], key=lambda w:get_word_score(w), reverse=True)
    
    # scoring function
    def update_score(self, grid):
        self.score = len(self.get_possible(grid))/(self.length**2)
        
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

