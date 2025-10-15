# word_trie.py

'''
constraints are 0-indexed: (0, 'a) means the first chr is 'a'

'''

from string import ascii_lowercase
from word_funcs import get_words_that_match
ALL_CHARS = ascii_lowercase
ALL_WORDS = sorted(open("words_alpha.txt").read().splitlines())
WORD_LEN_MIN = 3
# WORD_LEN_MAX = max([len(w) for w in ALL_WORDS])
WORD_LEN_MAX = 11

class Word_Trie:
    def __init__(self):
        self.children = {l: Node(l) for l in range(WORD_LEN_MIN, WORD_LEN_MAX+1)}
        
        for word in ALL_WORDS:
            self.add_word(word)
    
    def add_word(self, word):
        if not WORD_LEN_MIN <= len(word) <= WORD_LEN_MAX: return
        self.children[len(word)].add_word(word)
        
    def get_possibilities(self, length, constraints=[]):
        if not WORD_LEN_MIN <= length <= WORD_LEN_MAX: return []
        return self.children[length].get_possibilities(constraints)
        
class Node:
    def __init__(self, word_length, position_constraint=-1):
        self.words = []
        self.WORD_LENGTH = word_length
        self.POSITION_CONSTRAINT = position_constraint
        self.children = {position: {}
                         for position in range(self.POSITION_CONSTRAINT+1, self.WORD_LENGTH)}
    
    def add_word(self, word):
        self.words.append(word)
        for position in range(self.POSITION_CONSTRAINT+1, self.WORD_LENGTH):
            character = word[position]
            try:
                self.children[position][character].add_word(word)
            except KeyError:
                self.children[position][character] = Node(self.WORD_LENGTH, position)
        
    def get_possibilities(self, constraints):
        return self.words
    
class Word_Trie2:
    
    def __init__(self):
        self.words_with_length = {l: [] for l in range(WORD_LEN_MIN, WORD_LEN_MAX+1)}
        
        for word in ALL_WORDS:
            self.__add_word(word)
    
    def __add_word(self, word):
        if not WORD_LEN_MIN <= len(word) <= WORD_LEN_MAX: return
        self.words_with_length[len(word)].append(word)
        
    # TODO
    def get_possibilities(self, regex):
        length = len(regex)
        if not WORD_LEN_MIN <= length <= WORD_LEN_MAX: return []
        return get_words_that_match(regex, self.words_with_length[length])
        
if __name__ == '__main__':
    
    # from time import time
    # start = time()
    # trie = Word_Trie()
    # print(f"Time taken: {time()-start}")
    
    trie = Word_Trie2()
    print(trie.get_possibilities("*p*g*"))
    
    # from word_funcs import get_words_that_match
    # print(get_words_that_match("*y*y*y"))
    # print(trie.get_possibilities(6, [(1, 'y'), (3, 'y'), (5, 'y')]))
    # print(trie.children[6].children[1]['y'].words)
