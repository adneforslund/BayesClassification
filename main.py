# -*- encoding: utf-8 -*-
import codecs
import glob
import os
import re
import sys
import time
import pickle
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

negativeMean = 0
positiveMean = 0

# Wordcounts
def train(dirs):
    wordsTmp = []
    wordCounts = []
    out = {}
    print("Loading file contents...")
    for d in dirs:
        # Apner alle filer i en path,
        for file in glob.glob(str(d) + "/*.txt"):
            infile = open(file, encoding='utf-8', errors='ignore')
            a = infile.readline()
            a_rm = remove_tags(a)
            a_new = a_rm.lower()
            a_new = remove_punctuation(a_new)
            a_new = a_new.split(' ')
            for word in a_new:
                if len(word) < 3:
                    continue
                if d.name == "neg":
                    wordsTmp.append((word, 0))
                else:
                    wordsTmp.append((word, 1))

            infile.close()

    print("Getting unique words...")
    sys.stdout.flush()
    uniques = set(wordsTmp)
        
    print("Counting occurences...")
    sys.stdout.flush()
 
    count = Counter(wordsTmp)
    total = Counter(word[0] for word in wordsTmp)

    for (w, c) in uniques:
        wordCounts.append((w, (count[(w, 0)], total[w])))

    return dict(wordCounts)

# Words blir en liste med tuples (word, 0) eller (word, 1), hvor 0 er negativ og 1 er positiv

# Lagre ferdig trent classifier til senere bruk
def saveNBC(nbc, file_str):
    f = open(file_str, 'wb')
    pickle.dump(nbc, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()

# Laste ferdig trent classifier
def loadNBC(file_str):
    f = open(file_str, 'rb')
    nbc = pickle.load(f)
    f.close()
    return nbc



# rekner sannsynlighet
def probabilityPre(word, wordlist, c):
    (icl, tot) = wordlist[word]
    if c == 0 and tot > 0:
        return float(icl) / float(tot)
    elif c == 1 and tot > 0:
        return float(tot - icl) / float(tot)
    return -1.0

# rekner gjennomsnitt
def mean(c, wordlist):
    # print(wordlist)
    counter = 0
    total = 0
    for w, (i, j) in wordlist.items():
        if c == 0:
            counter += i
        elif c == 1:
            counter += j - i
        total += j
    return float(counter) / float(total)

# bayes regel : https://cdn-images-1.medium.com/max/1600/1*9YuCNcICo5PW5qqQug6Yqw.png


def bayes(a, b, pre):
    return (a*pre)/b
# tar et ord i en review, sjekker om den er positiv eller negativ


def classify(word, wordlist, positive, negative, c):
    if not word in wordlist:
        return -1.0
    pre = probabilityPre(word, wordlist, c)
    mean = 0
    if c == 1:
        mean = positive
    else:
        mean = negative
    print(mean)
    if pre == -1.0:
        return -1.0
    else:
        return bayes(0.5, mean, pre)

# for a fjerne html/xml tags med regex, erstatter med mellomrom . Funker med fakka formatering ogsa


def remove_tags(text):
    expression = re.compile(r'<[^>]+>')
    return expression.sub('', text)

# fjerner tulletegn fra en string


def remove_punctuation(text):
    for p in [',', '!', '"', '.', '?', ')', '(', '-', "'s", ":", ";"]:
        text = text.replace(p, '')
    return text

# tar en review, går ord for ord og gir sannsynlighet for at den er negativ eller positiv

def pather(path):
    new_path = Path(path)
    dirs = [x for x in new_path.iterdir() if x.is_dir() and x.name ==
            "neg" or x.name == "pos"]
    for d in dirs:
        print(d)
    sys.stdout.flush()
    return dirs

def reviewClassifier(review, wordlist, positive, negative, c):
    a_rm = remove_tags(review)
    a_new = a_rm.split(' ')
    sum = 0
    total = len(a_new)
    current = 0
    for word in a_new:
        current += 1
        loading = (current / total) * 100
        word = word.lower()
        word = remove_punctuation(word)
        prob = classify(word, wordlist, positive, negative, c)
        if prob != -1.0:
            sum += prob
        else:
            continue
    return sum / len(a_new)

class NBC:
    def __init__(self, positiveMean, negativeMean, training):
        self.negativeMean = positiveMean
        self.positiveMean = negativeMean
        self.training = training

# prøver å få til errorhandling, men tar alt som errors
def error_handler(parser, arg):
    if not os.path.exists(arg):
        parser.error("The path given: %s is not valid" % arg)
    else:
        return open(arg, 'r')

def main():
    isTest = False
    isClassify = False
    isTrain = False
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest = "myPath",
                        help="Give a path to your DATA directory, required", required = True
                        )
    parser.add_argument("-te", "--test", help="Read from file directory and run test metrics", required = False, action = 'store_true')
    parser.add_argument("-cl", "--classify", help="Classify one review given to stdin", required = False, action = 'store_true')
    parser.add_argument("-tr", "--train", help="Read from file directory to train the classifier", required = False, action = 'store_true')
    args = parser.parse_args()

    path = args.myPath
    if args.test:
        print("srat")
        isTest = True
    if args.classify:
        isClassify = True
    if args.train:
        isTrain = True
    
    try:
        dirs = pather(path)
    except FileNotFoundError:
        print("Invalid pathname, try again. ")
        sys.exit(0)

    if isTrain:
        start = time.time()
        nbc = train(dirs)
        positiveMean = mean(1, nbc)
        negativeMean = mean(0, nbc)
        nbc = NBC(positiveMean, negativeMean, nbc)
        saveNBC(nbc, "nbc.txt")
        print("Time used: {:.2f}s".format(time.time() - start))

    elif isTest:
        start = time.time() 
        nbc = loadNBC("nbc.txt")
        # Test her
        print("Time used: {:.2f}s".format(time.time() - start))

    elif isClassify:
        nbc = loadNBC("nbc.txt")
        print("Skriv inn ditt review:")
        stdin = input()
        start = time.time() 
        resultat = reviewClassifier(stdin, nbc.training, nbc.positiveMean, nbc.positiveMean, 0)
        print("Sjanse for at reviewet er negativt: {:.2f}%\nSjanse for at reviewet er positivt: {:.2f}%\nTid brukt: {:.2f}s".format(resultat * 100, (1 - resultat) * 100, time.time() - start))
        
main()
