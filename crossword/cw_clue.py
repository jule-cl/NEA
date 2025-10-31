from math import inf
from crossword.algorithms.word_funcs import get_words_that_match, get_word_score
from app_settings import *

class CW_Clue:
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
        