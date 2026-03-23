# bitboard.py

from copy import deepcopy

class Bitboard:
    """
    The class used to store a bitboard and convert the cells into binary, which then can be stored as an integer.
    
    Variables:
        __cells (list[tuple[int, int]]): A list containing cell coordinates which are included in the bitboard.
        __bb_size (int): The size of the overall bitboard, to determine where to pad the 0s.
        __bounds (dict): A dictionary recording the rows and column numbers of the edges of the bitboard pattern.
        __bitboard (int): The integer representing the bitboard. 
        
    Static Variables:
        EMPTY_CELL (const): Uses a 0 to represent an empty cell
        BLOCKED_CELL (const): Uses a 1 to represent an empty cell
        
    Methods:
        translate_bitboard: Called when the bitboard needs to be moved around in the grid.
        __update_bitboard: Called anytime the bitboard has been modified, e.g. translated, cell added
        add_cell: Adds a cell to the bitboard
        remove_cell: Removes a cell from the bitboard
        
    Getters:
        get_bit_board: Returns the integer representing the bitboard
    """
    EMPTY_CELL = 0
    BLOCKED_CELL = 1

    def __init__(self, cells, bb_size):
        """
        Initialises the bitbooard class.
        
        Args:
            cells: A list containing cell coordinates which are included in the bitboard.
            bb_size (int): The size of the overall bitboard, to determine where to pad the 0s.
        """
        self.__cells = cells
        self.__bb_size = bb_size
        
        self.__update_bitboard()
        
        self.__bounds = {'left': min([c[1] for c in cells]),
                         'right': max([c[1] for c in cells]),
                         'top': min([c[0] for c in cells]),
                         'bottom': max([c[0] for c in cells])}
        
    def translate_bitboard(self, rows, cols):
        """
        Translates the bitboard by r rows to the right and c columns down, and updates the bitboard .
        Negative values for rows and columns mean to the left and upwards respectively
        
        Args:
            rows (int): # of rows to the right to translate.
            col (int): # of columns down to translate.
        """
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
        """
        Updates the private variable __bitboard, the integer representing the bitboard
        """
        bb = ''
        for row in range(self.__bb_size):
            for col in range(self.__bb_size):
                if (row, col) in self.__cells: bb += str(Bitboard.BLOCKED_CELL)
                else: bb += str(Bitboard.EMPTY_CELL)
                
        self.__bitboard = int(bb, 2)
            
    def remove_cell(self, row, col):
        """
        Removes the cell specified from the bitboard and updates __bitboard
        
        Args:
            row (int): Row # of the cell to remove.
            col (int): Column # of the cell to remove.
        """
        self.__cells.remove((row, col))
        self.__update_bitboard()
    
    def add_cell(self, row, col):
        """
        Adds the cell specified from the bitboard and updates __bitboard
        
        Args:
            row (int): Row # of the cell to add.
            col (int): Column # of the cell to add.
        """
        self.__cells.append((row, col))
        self.__update_bitboard()
        
    def get_bit_board(self):
        """
        Returns the integer value currently stored in the private variable __bitboard
        """
        return self.__bitboard    
        