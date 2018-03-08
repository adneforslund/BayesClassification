from pathlib import Path
path = Path('DATA/aclImdb/train/')
dirs = [x for x in path.iterdir() if x.is_dir() and x.name == "neg" or x.name == "pos"]
for d in dirs:
    print(d)

import os
import glob
import re

from collections import Counter
import pandas as pd

# Words blir en liste med tuples (word, 0) eller (word, 1), hvor 0 er negativ og 1 er positiv 
words =[]


#for å fjerne html/xml tags med regex, erstatter med mellomrom . Funker med føkka formatering også
def remove_tags(text):
    expression = re.compile(r'<[^>]+>')
    return expression.sub('', text)


def remove_punctuation(text):
    for p in [',', '!', '"', '.', '?', ')', '(', '-', "'s"]:
        text = text.replace(p, '')
    return text

for d in dirs:
    # åpner alle filer i en path, renser og kopierer til en annen path
    for file in glob.glob(str(d) + "/*.txt"):
        print(file)
        infile = open(file)
        a = infile.readline()
        a_rm = remove_tags(a)
        a_new = a_rm.split(' ')
        for word in a_new:
            word = word.lower()
            word = remove_punctuation(word)
            if d.name == "neg":
                words.append((word, 0))
            else:
                words.append((word, 1))
            
        infile.close()

for word in words:
    print(word)
