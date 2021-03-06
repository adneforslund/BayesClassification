# -*- encoding: utf-8 -*-
import codecs
import glob
import os
import re
import sys
import time
import pickle
from math import log
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

negativeMean = 0
positiveMean = 0


def train(dirs):
    wordsTmp = []
    wordCounts = []
    out = {}
    print("Loading file contents...")
    for d in dirs:
        
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


def saveNBC(nbc, file_str):
    f = open(file_str, 'wb')
    pickle.dump(nbc, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()


def loadNBC(file_str):
    f = open(file_str, 'rb')
    nbc = pickle.load(f)
    f.close()
    return nbc




def probabilityPre(word, wordlist, c):
    (icl, tot) = wordlist[word]
    if c == 0 and tot > 0:
        return float(icl) / float(tot)
    elif c == 1 and tot > 0:
        return float(tot - icl) / float(tot)
    return -1.0


def mean(c, wordlist):
    
    counter = 0
    total = 0
    for w, (i, j) in wordlist.items():
        if c == 0:
            counter += i
        elif c == 1:
            counter += j - i
        total += j
    return float(counter) / float(total)


def bayes(a, b, pre):
    return (a*pre)/b


def classify(words, wordlist, positive, negative, c):
    probProductPos = 1.0
    probProductNeg = 1.0
    pre = 0.0
    for w in words:
        if not w in wordlist:
            continue
      
        pre = probabilityPre(w, wordlist, 1)
        if pre <= 0.0:
            pre = 1.0
        
        probProductPos *= pre

       
        pre = probabilityPre(w, wordlist, 0)
        if pre <= 0.0:
            pre = 1.0
      
        probProductNeg *= pre
          
    denom = probProductNeg * negative + probProductPos * positive
    num = 0
    
    if c == 1:
        num = probProductPos
        cl = positive
    else:
        num = probProductNeg
        cl = negative

    res = bayes(num, denom, cl)
    if res > 0.0:
        res = log(res)
    return res


def remove_tags(text):
    expression = re.compile(r'<[^>]+>')
    return expression.sub('', str(text))




def remove_punctuation(text):
    for p in [',', '!', '"', '.', '?', ')', '(', '-', "'s", ":", ";"]:
        text = text.replace(p, '')
    return text



def pather(path):
    new_path = Path(path)
    dirs = [x for x in new_path.iterdir() if x.is_dir() and x.name ==
            "neg" or x.name == "pos"]
    for d in dirs:
        print("Path found: {}".format(d))
    sys.stdout.flush()
    return dirs

def testAllReviews(nbc, testDirectory):
    totalCount = 0
    correctCount = 0
    
    for d in testDirectory:

        # Apner alle filer i en path,
        for file in glob.glob(str(d) + "/*.txt"):
            infile = open(file, encoding='utf-8', errors='ignore')
            a = infile.readline()
            a_rm = remove_tags(a)
            a_new = a_rm.lower()
            a_new = remove_punctuation(a_new)
            a_new = a_new.split(' ')
            if d.name == "neg" and reviewClassifier(a_new, nbc.training, nbc.positiveMean, nbc.negativeMean) < 0.5:
                correctCount+=1
            elif d.name == "pos" and reviewClassifier(a_new, nbc.training, nbc.positiveMean, nbc.negativeMean) > 0.5:
                correctCount+=1
            totalCount+=1

            infile.close()
    rate = float(correctCount) / float(totalCount) * 100

    return rate

def tidyWord(w):
    w = w.lower()
    return remove_punctuation(w)

def reviewClassifier(review, wordlist, positive, negative):
    a_rm = remove_tags(review)
    a_new = a_rm.split(' ')
    words = map(lambda w: tidyWord(w), a_new)
    neg = classify(words, wordlist, positive, negative, 0)
    pos = classify(words, wordlist, positive, negative, 1)
    relativeFreq = neg / (neg + pos)
    return relativeFreq

class NBC:
    def __init__(self, positiveMean, negativeMean, training):
        self.negativeMean = negativeMean
        self.positiveMean = positiveMean
        self.training = training


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
                        help="Give a path to your review directory, required", required = True
                        )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-te", "--test", help="Read from file directory and run test metrics", required = False, action = 'store_true')
    group.add_argument("-cl", "--classify", help="Classify one review given to stdin",
                       required=False, action='store_true')
    group.add_argument("-tr", "--train", help="Read from file directory to train the classifier",
                       required=False, action='store_true')
    args = parser.parse_args()

    path = args.myPath
    if args.test:
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
        print("Running classification training...")
        nbc = train(dirs)
        positiveMean = mean(1, nbc)
        negativeMean = mean(0, nbc)
        nbc = NBC(positiveMean, negativeMean, nbc)
        saveNBC(nbc, "nbc.txt")
        print("Done. Time used: {:.2f}s".format(time.time() - start))

    elif isTest:
        start = time.time()
        print("Loading training data...")
        nbc = loadNBC("nbc.txt")
        print("Running test classification. Please wait, do not turn off your computer...")
        rate = testAllReviews(nbc, dirs)
        print("Error rate: {:.2f}%\nTime used: {:.2f}s".format(100 - rate, time.time() - start))

    elif isClassify:
        nbc = loadNBC("nbc.txt")
        print("Skriv inn ditt review:")
        stdin = input()
        start = time.time() 
        res = reviewClassifier(stdin, nbc.training, nbc.positiveMean, nbc.negativeMean)
        if res < 0.5:
            print("The review is negative. Certainty: {:.2f}%".format((1 - res) * 100))
        else:
            print("The review is positive. Certainty: {:.2f}%".format(res * 100))
        print("Time used: {:.2f}s".format(time.time() - start))
        
        
main()
