# crossword_filler.py

# filling words in grid
EMPTY_CELL = 0
BLOCKED_CELL = 1

LETTERS_BY_FREQUENCY = "ETAOINSRHDLUCMFYWGPBVKXQJZ"
LETTER_FREQUENCIES = [12.02, 9.10, 8.12, 7.68, 7.31, 6.95, 6.28, 6.02, 5.92, 4.32, 3.98, 2.88, 
                      2.71, 2.61, 2.30, 2.11, 2.09, 2.03, 1.82, 1.49, 1.11, 0.69, 0.17, 0.11, 0.10]

# https://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html

class Crossword_filler:
    
    def __init__(self, constraints):
        """
        constraints = [[(0, 2), (0, 3), (1, 2), (1, 3)], 
                    [(-1, 0, -1, 1, -1),
                        (-1, 2, -1, 3, -1),
                        (-1, 0, -1, 2, -1),
                        (-1, 1, -1, 3, -1)
                        ]
                    ]
        is equivalent to
        #| |#| |#
        -+-+-+-+-
         | | | | 
        -+-+-+-+-
        #| |#| |#
        -+-+-+-+-
         | | | | 
        -+-+-+-+-
        #| |#| |#
        """

        self.__inter_constraints = constraints[0]
        self.__word_constraints = constraints[1]
        
        self.__intersections = [" " for _ in self.__inter_constraints]
        self.__words = ["" for _ in self.__word_constraints]

    def fill_grid(self):
        from random import randint, choice
        from string import ascii_uppercase
        from word_funcs import get_words_that_match
        
        for i in range(len(self.__intersections)):
            self.__intersections[i] = ascii_uppercase[randint(0, 25)]
            
        checked = set()
        for word_number, constraint in enumerate(self.__word_constraints):
            regex = ''.join(['*' if position == -1 else self.__intersections[position] for position in constraint])
            
            options = get_words_that_match(regex)
            if not options: 
                # need to rollback better
                continue
            self.__words[word_number] = choice(options)
                        
    def print_words(self):
        print(self.__words)
                
if __name__ == '__main__':
    constraints = [[(0, 2), (0, 3), (1, 2), (1, 3)], 
                   [(-1, 0, -1, 1, -1),
                    (-1, 2, -1, 3, -1),
                    (-1, 0, -1, 2, -1),
                    (-1, 1, -1, 3, -1)
                    ]
                   ]
    
    filler = Crossword_filler(constraints)
    filler.fill_grid()
    
    filler.print_words()


