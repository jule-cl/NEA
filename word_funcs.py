# word_funcs.py

# will try to move these funcs to a cpp file in the future

ALL_WORDS = sorted(open("words_alpha.txt").read().splitlines())

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
def get_words_that_match(regex, word_list=ALL_WORDS):
    from copy import deepcopy
    
    candidates = [w for w in ALL_WORDS if len(w)==len(regex)]
    
    for pos, letter in enumerate(regex):
        if letter == '*': continue
        candidates = [w for w in candidates if w[pos] == letter.lower()]
    
    return candidates
        
if __name__ == '__main__':
    # print(is_valid_word("syzygy"))
    print(get_words_that_match("*y*y*y"))