# word_funcs.py

# will try to move these funcs to a cpp file in the future
from functools import cache
ALL_WORDS = sorted(open("word_list.txt").read().splitlines())

LETTERS_BY_FREQUENCY = "ETAOINSRHDLUCMFYWGPBVKXQJZ"
LETTER_FREQUENCIES = [12.02, 9.10, 8.12, 7.68, 7.31, 6.95, 6.28, 6.02, 5.92, 4.32, 3.98, 2.88, 2.71,
                      2.61, 2.30, 2.11, 2.09, 2.03, 1.82, 1.49, 1.11, 0.69, 0.17, 0.11, 0.10, 0.07]
# https://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
LETTER_SCORE = {l:s for l, s in zip(LETTERS_BY_FREQUENCY, LETTER_FREQUENCIES)}

def is_valid_word(word):
    if word > ALL_WORDS[-1]: return False
    
    word = word.lower()
    left_pointer = 0
    right_pointer = len(ALL_WORDS)-1
    while left_pointer + 1 != right_pointer:
        next_pointer = (left_pointer+right_pointer)//2
        next_word = ALL_WORDS[next_pointer]
        
        if next_word == word:
            return True
        elif word > next_word:
            left_pointer = next_pointer
        elif word < next_word:
            right_pointer = next_pointer        
    
    if word == ALL_WORDS[left_pointer] or word == ALL_WORDS[right_pointer]: return True
    return False


# filtering method
@cache
def get_words_that_match(regex, word_list=ALL_WORDS):
    from copy import deepcopy
    
    candidates = [w for w in word_list if len(w)==len(regex)]
    
    for pos, letter in enumerate(regex):
        if letter == '*': continue
        candidates = [w for w in candidates if w[pos] == letter.lower()]
    
    return candidates

def get_word_score(word):
    return sum([LETTER_SCORE[c.upper()]for c in word])/len(word)
        
if __name__ == '__main__':
    # print(is_valid_word("syzygy"))
    print(len(get_words_that_match("***")))
    print(len(get_words_that_match("*********")))