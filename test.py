# test.py

"""
Used to parse the word_list file, calculating the scores of each word beforehand to avoid wasting time everytime upon loading app.
"""

from app_info import *
import json
from wordfreq import word_frequency
from functools import cache
from math import exp

def only_letters(w):
    output = ''
    for c in w:
        if c.isalpha(): output += c.upper()
    return output

@cache
def sigmoid(x):
    return 1 / (1 + exp(-x))

def get_displayed_score(word, read=True):
    """
    A lower score means the word isn't great (e.g. very long, not common)
    The autofill method will prioritise words with lower scores
    """

    base = WORD_POP[DISPLAYED_TO_WORD[word]] # popularity of the word
    weight_a = sigmoid(-len(word)) # length of the word
    weight_b = (len(DISPLAYED_TO_WORD[word]) - len(word)) # non-letter characters e.g. spaces, hyphens
    weight_c = 1-sum([LETTER_SCORE[c] for c in word])/len(word) # average letter freqency: 0-1, lower is more common
    
    return Weights.WEIGHT_BASE * base + Weights.WEIGHT_A * weight_a + Weights.WEIGHT_B * weight_b + Weights.WEIGHT_C * weight_c


if __name__ == '__main__':
    with open("word_list.txt") as file:
        ALL_WORDS = []; ALL_DISPLAYED = []
        DISPLAYED_TO_WORD = {}
        WORD_TO_DISPLAYED = {}
        for word in file.read().splitlines():
            if "$" in word: continue    
            word = word.upper()
            displayed = only_letters(word)
            ALL_DISPLAYED.append(displayed)
            DISPLAYED_TO_WORD[displayed] = word
            WORD_TO_DISPLAYED[word] = displayed

    LETTERS_BY_FREQUENCY = "ETAOINSRHDLUCMFYWGPBVKXQJZ"
    LETTER_FREQUENCIES = [12.02, 9.10, 8.12, 7.68, 7.31, 6.95, 6.28, 6.02, 5.92, 4.32, 3.98, 2.88, 2.71,
                        2.61, 2.30, 2.11, 2.09, 2.03, 1.82, 1.49, 1.11, 0.69, 0.17, 0.11, 0.10, 0.07]
    # https://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
    LETTER_SCORE = {l:s/100 for l, s in zip(LETTERS_BY_FREQUENCY, LETTER_FREQUENCIES)}
    WORD_POP = {DISPLAYED_TO_WORD[word]: 1-word_frequency(word, "en") for word in ALL_DISPLAYED} # lower number -> more common
    WORD_INFO = {DISPLAYED_TO_WORD[word]: {"score": get_displayed_score(word), "displayed": word} for word in ALL_DISPLAYED if word}
    
    with open(WORD_DATA_FILE, "w") as f:
        json.dump([LETTER_SCORE, WORD_INFO], f, indent=4)