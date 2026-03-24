# cw_clue.py

from math import inf
from word_funcs import Word_Funcs
from app_info import *

class CW_Clue:
    """
    Represents a single clue in a crossword puzzle, storing its position, direction, word content, and meta data used during autofill.

    Variables:
        row (int): Row index of the first cell of the clue.
        col (int): Column index of the first cell of the clue.
        direction (str): Direction of the clue, either 'A' (across) or 'D' (down).
        length (int): Number of cells in the clue.
        clue_length (str): Displayed length string, e.g. "(4, 7)" for multi-word answers.
        clue_number (int): The number assigned to this clue in the grid.
        word (str): The current letters placed in this clue's cells.
        clue_sentence (str): The clue text written by the user.
        parent_grid (Crossword): The crossword object this clue belongs to.
        cells (list[tuple[int, int]]): List of (row, col) positions for each cell in the clue.
        intersections (set[CW_Clue]): Set of clues that intersect with this clue.
        intersection_positions (list[int]): Indices within this clue's cells where intersections occur.
        attempts (int): Number of words attempted for this clue during autofill.
        used_words (set[str]): Words that have already been placed elsewhere in the grid.
        failed_words (set[str]): Words that have been tried and failed for this clue.
        score (float): Priority score used by the autofill algorithm; lower means more constrained.

    Methods:
        get_possible_words: Returns a filtered, sorted list of valid candidate words.
        update_score: Recalculates the priority score based on current candidates.
        change_letter: Updates a single letter in the word at the given grid position.
        other_direction: Static method that returns the opposite direction to the one given.
    """
    def __init__(self, parent_grid, row, col, direction, length, clue_number, word="", clue_sentence=""):
        """
        Initialises a CW_Clue instance with its position, direction, and metadata.

        Args:
            parent_grid (Crossword): The crossword object this clue belongs to.
            row (int): Row index of the first cell of the clue.
            col (int): Column index of the first cell of the clue.
            direction (str): Direction of the clue, either 'A' (across) or 'D' (down).
            length (int): Number of cells in the clue.
            clue_number (int): The number assigned to this clue in the grid.
            word (str): The initial word content. Defaults to empty cells if not provided.
            clue_sentence (str): The clue text written by the user. Defaults to an empty string.
        """
        self.row = row
        self.col = col
        self.direction = direction
        self.length = length
        self.clue_length = str(length)
        self.clue_number = clue_number
        self.word = word if word else EMPTY_CELL*length
        self.clue_sentence = clue_sentence
        self.parent_grid = parent_grid
        self.__update_clue_length()
        
        self.intersections = set()
        self.intersection_positions = []
        
        if direction == 'A': d_row, d_col = 0, 1
        if direction == 'D': d_row, d_col = 1, 0
        self.cells = [(row+d_row*i, col+d_col*i) for i in range(length)]
        
        self.attempts = 0
        self.used_words = set()
        self.failed_words = set()
        self.score = inf
        
    def __get_regex(self, intersections_only=False):
        """
        Builds a regex pattern from the current word, replacing empty cells with '*'.
        If intersections_only is True, then the regex is created ingoring the other letters.

        Returns:
            str: A pattern string where empty cells are represented as '*'.
        """
        if not intersections_only:
            return ''.join(['*' if c==EMPTY_CELL else c for c in self.word])
        else:
            return ''.join(['*' if c==EMPTY_CELL or index not in self.intersection_positions else c for index, c in enumerate(self.word)])
    
    def get_possible_words(self, intersections_only=False):
        """
        Returns a sorted, filtered list of valid candidate words for this clue based on the current letter pattern, 
        excluding used and previously failed words.
        If intersections_only is True, then the regex is created ingoring the other letters. Used to find alternate words.

        Returns:
            list[str]: Candidate words sorted by word score, with used and failed words removed.
        """
        regex = self.__get_regex(intersections_only)
        candidates = sorted([w for w in Word_Funcs.get_words_that_match(regex)], key=lambda w:Word_Funcs.get_word_score(w))
        candidates = list(filter(lambda w: w not in self.used_words, candidates))
        candidates = list(filter(lambda w: w not in self.failed_words, candidates))
        return candidates
    
    def update_score(self):
        """
        Recalculates the priority score for this clue based on its current candidates.
        A score of 0 means no candidates exist. 
        A score of 1 means only one candidate remains. 
        Otherwise the score is a weighted combination of the top two candidates' word scores, giving lower scores to more constrained clues.
        """
        candidates = self.get_possible_words()
        if not candidates: self.score = 0
        elif len(candidates) == 1: self.score = 1
        else: self.score = Weights.WEIGHT_1 * Word_Funcs.get_word_score(candidates[0]) + Weights.WEIGHT_2 * Word_Funcs.get_word_score(candidates[1])
        
    def change_letter(self, row, col, letter, update_length=False):
        """
        Updates a single letter in the clue's word at the given grid position.

        Args:
            row (int): Row index of the cell to update.
            col (int): Column index of the cell to update.
            letter (str): The new letter to place at the given position.
            update_length (bool): Whether to recalculate the displayed clue length. Defaults to False.
        """
        position = (row-self.row) + (col-self.col)
        self.word = self.word[:position] + letter + self.word[position+1:]
        if update_length: self.__update_clue_length()
        
    def __update_clue_length(self):
        """
        Recalculates and updates the displayed clue length string based on the current word.
        """
        self.clue_length = Word_Funcs.get_clue_length(Word_Funcs.displayed_to_word(self.word))

    def other_direction(dir):
        """
        Returns the opposite direction to the one given.

        Args:
            dir (str): A direction, either 'A' (across) or 'D' (down).

        Returns:
            str: 'A' if dir is 'D', or 'D' if dir is 'A'.
        """
        return 'A' if dir == 'D' else 'D'
