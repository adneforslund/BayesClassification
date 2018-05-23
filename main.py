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

negative_mean = 0
positive_mean = 0

def in_vocabulary(word, vocabulary):
    if word in vocabulary:
        return True
    else:
        return False

def train(path):
    words_temp = []
    words_count = []
    out = {}
    print("Loading file contents...")
    toktok = ToktokTokenizer()

    try:
        dirs = pather(path + "/train")
        vocabulary = set(open(str(path) + "imdb.vocab", encoding='utf-8', errors='ignore').read().splitlines())
    except FileNotFoundError:
        print("Invalid pathname, try again. ")
        sys.exit(0)

    print("Loaded paths and vocabulary from data folder.")
    print("Running training, this may take a while...") 

    for directory in dirs:
        print("Training from directory: " + directory.name) 
        for file in glob.glob(str(directory) + "/*.txt"):
            infile = open(file, encoding='utf-8', errors='ignore')
            line = infile.readline()
            tokens = split(line)
            for word in tokens:
                if len(word) < 3 or not in_vocabulary(word, vocabulary):
                    continue
                if directory.name == "neg":
                    words_temp.append((word, 0))
                else:
                    words_temp.append((word, 1))

            infile.close()

    print("Getting unique words...")
    sys.stdout.flush()
    uniques = set(words_temp)
        
    print("Counting occurences...")
    sys.stdout.flush()
 
    count = Counter(words_temp)
    total = Counter(word[0] for word in words_temp)

    for (w, c) in uniques:
        words_count.append((w, (count[(w, 0)], total[w])))


    return dict(words_count)


class NBC:
    def __init__(self, positive_mean, negative_mean, training):
        self.negative_mean = negative_mean
        self.positive_mean = positive_mean
        self.training = training

def save_NBC(nbc, file_str):
    f = open(file_str, 'wb')
    pickle.dump(nbc, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()

# reads the NBC file for classifying reviews.
def load_nbc(file_str):
    f = open(file_str, 'rb')
    nbc = pickle.load(f)
    f.close()
    return nbc




def probability_pre(word, word_list, c):
    if word in word_list:
        (icl, tot) = word_list[word]
        if c == 0 and tot > 0:
            return float(icl) / float(tot)
        elif c == 1 and tot > 0:
            return float(tot - icl) / float(tot)
    return -1.0


def mean(c, word_list):
    
    counter = 0
    total = 0
    for w, (i, j) in word_list.items():
        if c == 0:
            counter += i
        elif c == 1:
            counter += j - i
        total += j
    return float(counter) / float(total)

# bayes theorem
def bayes(a, b, pre):
    return (a*pre)/b


def classify(words, word_list, positive, negative, c):
    probability_product_positive = 1.0
    probability_product_negative = 1.0
    pre = 1.0

    if len(words) == 0:
        return -1.0

    for w in words: 
        if len(w) < 3:
            continue
        pre = probability_pre(w, word_list, 1)
        if pre <= 0.0:
            pre = 1.0
        
        probability_product_positive *= pre
       
        pre = probability_pre(w, word_list, 0)
        if pre <= 0.0:
            pre = 1.0
      
        probability_product_negative *= pre
   
    denom = probability_product_negative * negative + probability_product_positive * positive
   
    num = 0
    
    if c == 1:
        num = probability_product_positive
        cl = positive
    else:
        num = probability_product_negative
        cl = negative

    if denom > 0.0:
        res = bayes(num, denom, cl)
    else:
        return -1.0
    if res > 0.0:
        res = log(res)
    else:
        return -1.0
    return res

# removes HTML/XML tags from string
def split(text):
    expression = re.compile("[\w'|\w]+")
    return expression.findall(str(text))

# removes special characters from string
def remove_punctuation(text):
    for p in [',', '!', '"', '.', '?', ')', '(', '-', "'s", ":", ";"]:
        text = text.replace(p, '')
    return text


# iterates through all files in a given path
def pather(path):
    new_path = Path(path)
    directories = [x for x in new_path.iterdir() if x.is_dir() and x.name ==
            "neg" or x.name == "pos"]
    for d in directories:
        print("Path found: {}".format(d))
    sys.stdout.flush()
    return directories

def testAllReviews(nbc, path):
    toktok = ToktokTokenizer()    
    try:
        dirs = pather(path + "/test")
    except FileNotFoundError:
        print("Invalid pathname, try again. ")
        sys.exit(0)
    totalCount = 0
    correctCount = 0
    

    for directory in dirs:
        # Apner alle filer i en path,
        print("Testing from directory: " + str(directory))
        for file in glob.glob(str(directory) + "/*.txt"):
            infile = open(file, encoding='utf-8', errors='ignore')
            line = infile.readline()
            words = split(line)

            classification = reviewClassifier(words, nbc.training, nbc.positive_mean, nbc.negative_mean)

            if classification == -1.0:
                 continue
            elif directory.name == "neg" and classification < 0.5:
                correctCount+=1
            elif directory.name == "pos" and classification > 0.5:
                correctCount+=1
            totalCount+=1

            infile.close()
    rate = float(correctCount) / float(totalCount) * 100

    return rate
# makes everything lower case
def tidyWord(w):
    w = w.lower()
    return remove_punctuation(w)

def reviewClassifier(review, word_list, positive, negative):
    neg = classify(review, word_list, positive, negative, 0)
    pos = classify(review, word_list, positive, negative, 1)
    if neg == -1.0 or pos == -1.0:
       relativeFreq = -1.0
    else:
       relativeFreq = neg / (neg + pos)
    return relativeFreq

def error_handler(parser, arg):
    if not os.path.exists(arg):
        parser.error("The path given: %s is not valid" % arg)
    else:
        return open(arg, 'r')

# main method
def main():
    is_test = False
    is_classify = False
    is_train = False
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest = "myPath",
                        help="Give a path to dataset directory, required", required = True
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
        is_test = True
    if args.classify:
        is_classify = True
    if args.train:
        is_train = True
    

    if is_train:
        start = time.time()
        print("Running classification training...")
        nbc = train(path)
        positive_mean = mean(1, nbc)
        negative_mean = mean(0, nbc)
        nbc = NBC(positive_mean, negative_mean, nbc)
        save_NBC(nbc, "nbc.txt")
        print("Done. Time used: {:.2f}s".format(time.time() - start))

    elif is_test:
        start = time.time()
        print("Loading training data...")
        nbc = load_nbc("nbc.txt")
        print("Running test classification. Please wait, do not turn off your computer...")
        rate = testAllReviews(nbc, path)
        print("Error rate: {:.2f}%\nTime used: {:.2f}s".format(100 - rate, time.time() - start))

    elif is_classify:
        nbc = load_nbc("nbc.txt")
        print("Skriv inn ditt review:")
        stdin = input()
        start = time.time() 
        res = reviewClassifier(stdin, nbc.training, nbc.positive_mean, nbc.negative_mean)
        if res == -1.0:
            print("The review could not be read, doesn't contain any known words")
        elif res < 0.5:
            print("The review is negative. Certainty: {:.2f}%".format((1 - res) * 100))
        else:
            print("The review is positive. Certainty: {:.2f}%".format(res * 100))
        print("Time used: {:.2f}s".format(time.time() - start))
        
        
main()
