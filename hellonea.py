import re

ALL_WORDS = []

f = open("words_alpha.txt").read()
ALL_WORDS = f.splitlines()

maxlen = max(map(len, ALL_WORDS))
counts = {t: len([x for x in ALL_WORDS if len(x) == t]) for t in range(1, maxlen+1)}

print(counts)
    
