# -*- coding: utf-8 -*-
import codecs
import glob
import os
import re
import sys
import time
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

negativeMean = 0
positiveMean = 0

words = []
wordsTmp = []
wordCounts = []


# Words blir en liste med tuples (word, 0) eller (word, 1), hvor 0 er negativ og 1 er positiv

# rekner sannsynlighet


def probabilityPre(word, wordlist, c):
    for (w, c, icl, tot) in wordlist:
        if w == word and tot > 0:
            return float(icl) / float(tot)
    return -1.0
# rekner gjennomsnitt


def mean(c, wordlist):
    counter = 0
    total = 0
    for (w, cl, i, j) in wordlist:
        if c == cl:
            counter += i
        total += j
    return float(counter) / float(total)

# bayes regel : https://cdn-images-1.medium.com/max/1600/1*9YuCNcICo5PW5qqQug6Yqw.png


def bayes(a, b, pre):
    return (a*pre)/b
# tar et ord i en review, sjekker om den er positiv eller negativ


def classify(word, wordlist, c):
    pre = probabilityPre(word, wordlist, c)
    mean = 0
    if c == 1:
        mean = positiveMean
    else:
        mean = negativeMean
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

def reviewClassifier(review, wordlist, c):
    a_rm = remove_tags(review)
    a_new = a_rm.split(' ')
    sum = 0
    total = len(a_new)
    current = 0
    for word in a_new:
        current += 1
        loading = (current / total) * 100
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" + str(int(loading)) + "%")
        word = word.lower()
        word = remove_punctuation(word)
        prob = classify(word, wordlist, c)
        if prob != -1.0:
            sum += prob
        else:
            continue
    return sum / len(a_new)


def error_handler(parser, arg):
    if not os.path.exists(arg):
        parser.error("The path given: %s is not valid" % arg)
    

def main():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="myPath",
                        help="Give a path to your DATA directory",
                        type = lambda x: error_handler(parser,x))
    args = parser.parse_args()
    path = args.myPath
    pather(path)
 #   text = open(myFile)
 #   print(text.read())


main()
