# word_funcs.py

from functools import cache
import json
from app_info import *
import requests

class Word_Funcs:
    """
    Utility methods for working with words.
    Word data is loaded from a JSON file at class definition time.

    Variables:
        LETTER_SCORE (dict): Scores for individual letters.
        WORD_INFO (dict): Full word metadata keyed by word string.
        ALL_DISPLAYED (list[str]): List of all displayed word forms.
        DISPLAYED_TO_WORD (dict): Maps displayed forms back to their base word.
        DISPLAYED_SCORES (dict): Maps displayed forms to their score.

    Methods:
        only_letters: Strips non-alphabetic characters and uppercases the result.
        get_words_that_match: Returns all words matching a given letter pattern.
        get_word_score: Returns the score for a displayed word form.
        get_definition: Fetches definitions for a word from an online dictionary API.
        displayed_to_word: Returns the base word for a given displayed form.
        get_clue_length: Returns a formatted clue length string for a given word.
    """
    
    """
    Reads the data from word_data.json
    This avoids calculating scores and parsing the word list every time the app is run.
    """
    with open(WORD_DATA_FILE, "r") as f:
        data = json.load(f)
        LETTER_SCORE = data[0]
        WORD_INFO = data[1]
        ALL_DISPLAYED = [info["displayed"] for info in WORD_INFO.values()]
        DISPLAYED_TO_WORD = {info["displayed"]: word for word, info in WORD_INFO.items()}
        DISPLAYED_SCORES = {info["displayed"]: info["score"] for info in WORD_INFO.values()}
        
    def only_letters(w):
        """
        Strips all non-alphabetic characters from a string and returns it uppercased.

        Args:
            w (str): The input string.

        Returns:
            str: The input with only alphabetic characters, uppercased.
        """
        output = ''
        for c in w:
            if c.isalpha(): output += c.upper()
        return output
    
    @cache
    def get_words_that_match(regex, word_list=ALL_DISPLAYED):
        """
        Returns a list of all words from the word list that match the given pattern.
        '*' in the pattern matches to any letter at that position.

        Args:
            regex (str): A pattern string where '*' matches to any character.
            word_list (tuple[str]): The list of words to search. Uses ALL_DISPLAYED
            
        Returns:
            list[str]: A list of all words matching the pattern.
        """
        candidates = [w for w in word_list if len(w)==len(regex)]
        
        for pos, letter in enumerate(regex):
            if letter == '*': continue
            candidates = [w for w in candidates if w[pos] == letter.upper()]
        
        return candidates

    def get_word_score(word):
        """
        Returns the score for the given displayed word form. 
        A lower score means the word should be prioritised in the autofill algorithm.
        It reads from the data in the word_data.json file, to avoid calculating the score every time the app is run.

        Args:
            word (str): The displayed word form to score.

        Returns:
            float: The score for the word.
        """
        return Word_Funcs.DISPLAYED_SCORES[word]

    @cache
    def get_definition(word):
        """
        Fetches definitions for the given word from the Free Dictionary API.
        Returns a list of definition entries, each containing a part of speech and definition text.

        Args:
            word (str): The word to look up.

        Returns:
            list[dict] or None: A list of dicts with 'pos' and 'definition' keys, or None if the word was not found or the request failed.
        """
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
        Returns the base word corresponding to the given displayed form.
        If no match is found, returns the displayed form unchanged.

        Args:
            displayed (str): The displayed form of the word to look up.

        Returns:
            str: The base word, or the displayed form if no match exists.
        """
        try:
            v = Word_Funcs.DISPLAYED_TO_WORD[displayed]
        except KeyError:
            v = displayed
        return v
    
    @cache
    def get_clue_length(word):
        """
        Returns a formatted clue length string for the given word, accounting for hyphens and spaces. 
        For example, "well-known" returns "4-5" and "ice cream" returns "3, 5".

        Args:
            word (str): The word to format a length string for.

        Returns:
            str: The formatted clue length string.
        """
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
