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
        self.intersections = []
        self.intersection_positions = []
        
        self.possible_words = []
        self.current_attempt = 0
        self.failed_words = []
        
        self.score = inf
        
    def __get_regex(self):
        return ''.join(['*' if (c:=self.parent_grid.grid[row][col])==EMPTY_CELL else c for (row, col) in self.cells])
    
    def get_possible_words(self):
        regex = self.__get_regex()
        candidates = sorted([w.upper() for w in get_words_that_match(regex)], key=lambda w:get_word_score(w), reverse=True)
        candidates = list(filter(lambda w: w not in self.parent_grid.used_words, candidates)) # filter out used words
        candidates = list(filter(lambda w: w not in self.failed_words, candidates)) # filter out failed words
        return candidates
    
    def update_possible_words(self, constraint):
        regex = self.__get_regex()
        self.possible_words = sorted([w.upper() for w in get_words_that_match(regex)], key=lambda w:get_word_score(w), reverse=True)
        self.possible_words = list(filter(lambda w: w not in self.parent_grid.used_words, self.possible_words)) # filter out used words
        self.possible_words = self.possible_words[:constraint]
    
    # based off patterns rather than words
    def update_score(self):
        if not self.get_possible_words(): self.score = 0
        else: self.score = get_word_score(self.get_possible_words()[0])
        