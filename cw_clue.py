from math import inf
from word_funcs import get_words_that_match, get_word_score
from app_settings import *

class CW_Clue:
    def __init__(self, row, col, direction, length, cells, parent_grid):
        self.row = row
        self.col = col
        self.direction = direction
        self.length = length 
        self.parent_grid = parent_grid
        
        self.cells = cells
        self.intersections = set()
        self.intersection_positions = []
        
        self.attempts = 0
        self.failed_words = []
        
        self.score = inf
        
    def __get_regex(self):
        return ''.join(['*' if (c:=self.parent_grid.grid[row][col])==EMPTY_CELL else c for (row, col) in self.cells])
    
    def get_possible_words(self):
        regex = self.__get_regex()
        candidates = sorted([w.upper() for w in get_words_that_match(regex)], key=lambda w:get_word_score(w))
        candidates = list(filter(lambda w: w not in self.parent_grid.used_words, candidates)) # filter out used words
        candidates = list(filter(lambda w: w not in self.failed_words, candidates)) # filter out failed words
        return candidates
    
    # based off patterns rather than words
    def update_score(self):
        # uses word score to calculate, and gives a lower score to longer words, which prioritises them
        if not self.get_possible_words(): self.score = 0
        else: self.score = len(self.get_possible_words())
        