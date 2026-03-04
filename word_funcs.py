# word_funcs.py

from functools import cache
from math import log
import requests

class Word_Funcs:

    def only_letters(w):
        output = ''
        for c in w:
            if c.isalpha(): output += c.upper()
        return output

    with open("word_list.txt") as file:
        ALL_DISPLAYED = []
        DISPLAYED_TO_WORD = {}
        for word in file.read().splitlines():
            word = word.upper()
            displayed = only_letters(word)
            try:
                DISPLAYED_TO_WORD[displayed] += [word]
            except KeyError:
                DISPLAYED_TO_WORD[displayed] = [word]
                ALL_DISPLAYED.append(displayed)

    LETTERS_BY_FREQUENCY = "ETAOINSRHDLUCMFYWGPBVKXQJZ"
    LETTER_FREQUENCIES = [12.02, 9.10, 8.12, 7.68, 7.31, 6.95, 6.28, 6.02, 5.92, 4.32, 3.98, 2.88, 2.71,
                        2.61, 2.30, 2.11, 2.09, 2.03, 1.82, 1.49, 1.11, 0.69, 0.17, 0.11, 0.10, 0.07]
    # https://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
    LETTER_SCORE = {l:s/100 for l, s in zip(LETTERS_BY_FREQUENCY, LETTER_FREQUENCIES)}
    WORD_POP = {word: index+1 for index, word in enumerate(ALL_DISPLAYED)}

    # filtering method
    @cache
    def get_words_that_match(regex, word_list=ALL_DISPLAYED):
        candidates = [w for w in word_list if len(w)==len(regex)]
        
        for pos, letter in enumerate(regex):
            if letter == '*': continue
            candidates = [w for w in candidates if w[pos] == letter.upper()]
        
        return candidates

    # uses popularity of word and the average letter frequency of the word
    @cache
    def get_word_score(word):
        base = log(Word_Funcs.WORD_POP[word])+1 # popularity of the word
        weight_a = len(word) # length of the word
        weight_b = (len(Word_Funcs.DISPLAYED_TO_WORD[word]) - len(word) + 1) # non-letter characters e.g. spaces, hyphens
        weight_c = sum([Word_Funcs.LETTER_SCORE[c] for c in word])/len(word) # average letter freqency: 0-1
        
        return 20-weight_a

    @cache
    def get_definition(word):
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                definitions = []
                for entry in data:
                    for meaning in entry.get('meanings', []):
                        pos = meaning.get('partOfSpeech', '')
                        for definition in meaning.get('definitions', []):
                            definition = definition.get('definition', '')
                            
                            definitions.append({'pos': pos, 'definition': definition})
                            
                return definitions
            
            else: return None
            
        except: return None
        
    def displayed_to_word(displayed):
        """
        returns lists of words which the displayed word can possibly correspond to.
        """
        try:
            v = Word_Funcs.DISPLAYED_TO_WORD[displayed]
        except KeyError:
            v = []
        return v

if __name__ == '__main__':
    for i in range(1, 30):
        print(i, len([c for c in Word_Funcs.ALL_DISPLAYED if len(c)==i]))
