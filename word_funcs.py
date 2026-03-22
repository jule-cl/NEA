# word_funcs.py

from functools import cache
import json
from app_info import *
import requests

class Word_Funcs:
    with open(WORD_DATA_FILE, "r") as f:
        data = json.load(f)
        LETTER_SCORE = data[0]
        WORD_INFO = data[1]
        ALL_DISPLAYED = [info["displayed"] for info in WORD_INFO.values()]
        DISPLAYED_TO_WORD = {info["displayed"]: word for word, info in WORD_INFO.items()}
        DISPLAYED_SCORES = {info["displayed"]: info["score"] for info in WORD_INFO.values()}
        
    def only_letters(w):
        output = ''
        for c in w:
            if c.isalpha(): output += c.upper()
        return output
    
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
        """
        A lower score means the word isn't great (e.g. very long, not common)
        The autofill method will prioritise words with lower scores
        """
        return Word_Funcs.DISPLAYED_SCORES[word]

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
        Returns which word the displayed word corresponds to, if it exists.
        """
        try:
            v = Word_Funcs.DISPLAYED_TO_WORD[displayed]
        except KeyError:
            v = displayed
        return v
    
    @cache
    def get_clue_length(word):
        clue_length = ""
        section_length = 0
        for char in word:
            if char == '-':
                clue_length += f"{section_length}-"
                section_length = 0
            elif char == ' ':
                clue_length += f"{section_length}, "
                section_length = 0
            else:
                section_length += 1
        clue_length += str(section_length)
                
        return clue_length

if __name__ == '__main__':
    print(Word_Funcs.get_word_score("OUT"))
