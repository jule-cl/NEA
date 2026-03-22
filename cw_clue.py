from math import inf
from word_funcs import Word_Funcs
from app_info import *

class CW_Clue:
    def __init__(self, parent_grid, row, col, direction, length, clue_number, word="", clue_sentence=""):
        self.row = row
        self.col = col
        self.direction = direction # 'A' or 'D'
        self.length = length
        self.clue_length = str(length) # this is what is displayed e.g. (4, 7)
        self.clue_number = clue_number # int
        self.word = word if word else EMPTY_CELL*length
        self.clue_sentence = clue_sentence
        self.parent_grid = parent_grid
        self.__update_clue_length()
        
        self.intersections = set()
        self.intersection_positions = []
        
        if direction == 'A': d_row, d_col = 0, 1
        if direction == 'D': d_row, d_col = 1, 0
        self.cells = [(row+d_row*i, col+d_col*i) for i in range(length)]
        
        # used for autofill
        self.attempts = 0
        self.used_words = set()
        self.failed_words = set() # includes failed words
        self.score = inf
        
    def __get_regex(self):
        return ''.join(['*' if c==EMPTY_CELL else c for c in self.word])
    
    def get_possible_words(self):
        regex = self.__get_regex()
        candidates = sorted([w for w in Word_Funcs.get_words_that_match(regex)], key=lambda w:Word_Funcs.get_word_score(w))
        candidates = list(filter(lambda w: w not in self.used_words, candidates)) # filter out used words
        candidates = list(filter(lambda w: w not in self.failed_words, candidates)) # filter out failed words
        return candidates
    
    # based off patterns rather than words
    def update_score(self):
        # uses word score to calculate, and gives a lower score to longer words, which prioritises them
        candidates = self.get_possible_words()
        if not candidates: self.score = 0
        elif len(candidates) == 1: self.score = 1
        else: self.score = Weights.WEIGHT_1 * Word_Funcs.get_word_score(candidates[0]) + Weights.WEIGHT_2 * Word_Funcs.get_word_score(candidates[1])
        
    def change_letter(self, row, col, letter, update_length=False):
        position = (row-self.row) + (col-self.col)
        self.word = self.word[:position] + letter + self.word[position+1:]
        if update_length: self.__update_clue_length()
        
    def __update_clue_length(self):
        self.clue_length = Word_Funcs.get_clue_length(Word_Funcs.displayed_to_word(self.word))

    def other_direction(dir):
        return 'A' if dir == 'D' else 'D'

        