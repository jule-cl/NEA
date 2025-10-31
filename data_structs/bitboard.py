# bitboard.py

from copy import deepcopy

class Bitboard:
    EMPTY_CELL = 0
    BLOCKED_CELL = 1
    
    def __init__(self, cells, bb_size):
        self.__cells = cells
        self.__bb_size = bb_size
        
        self.__update_bitboard()
        
        self.__bounds = {'left': min([c[1] for c in cells]),
                         'right': max([c[1] for c in cells]),
                         'top': min([c[0] for c in cells]),
                         'bottom': max([c[0] for c in cells])}
        
    def translate_bitboard(self, rows, cols):
        
        if self.__bounds['left'] + cols < 0 or self.__bounds['right'] + cols > self.__bb_size-1 or \
            self.__bounds['top'] + rows < 0 or self.__bounds['bottom'] + rows > self.__bb_size-1:
                raise Exception("out of bounds")
            
        self.__bounds['left'] += cols
        self.__bounds['right'] += cols
        self.__bounds['top'] += rows
        self.__bounds['bottom'] += rows
        
        new_cells = []
        for (row, col) in self.__cells:
            new_cells.append((row+rows, col+cols))
            
        self.__cells = deepcopy(new_cells)
        
        self.__update_bitboard()
        
    def __update_bitboard(self):
        bb = ''
        for row in range(self.__bb_size):
            for col in range(self.__bb_size):
                if (row, col) in self.__cells: bb += str(Bitboard.BLOCKED_CELL)
                else: bb += str(Bitboard.EMPTY_CELL)
                
        self.__bitboard = int(bb, 2)
            
    def remove_cell(self, row, col):
        self.__cells.remove((row, col))
        self.__update_bitboard()
    
    def add_cell(self, row, col):
        self.__cells.append((row, col))
        self.__update_bitboard()
        
    def get_bit_board(self):
        return self.__bitboard
        
        