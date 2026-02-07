from app_settings import *

class Clue:
    def __init__(self, parent_grid, first_row, first_col, direction, length, word=""):
        self.first_row = first_row
        self.first_col = first_col
        self.direction = direction
        self.length = length
        self.word = word if word else EMPTY_CELL*length
        self.parent_grid = parent_grid
        
        if direction == 'A': d_row, d_col = 0, 1
        if direction == 'D': d_row, d_col = 1, 0
        self.cells = {(first_row+d_row*i, first_col+d_col*i) for i in range(length)}
        
    def change_letter(self, row, col, letter):
        position = (row-self.first_row) + (col-self.first_col)
        self.word = self.word[:position] + letter + self.word[position+1:]
        
        