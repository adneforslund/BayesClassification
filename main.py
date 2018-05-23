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

# for traing the program on the train set
def train(directories):
    words_temp = []
    words_count = []
    out = {}
    print("Loading file contents...")
    for d in directories:
        
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

# makes a NBC file with results from the training, to be read later.
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
    pre = 0.0
    for w in words:
        if not w in word_list:
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

    result = bayes(num, denom, cl)
    if result > 0.0:
        result = log(result)
    return result

# removes HTML/XML tags from string
def remove_tags(text):
    expresultsion = re.compile(r'<[^>]+>')
    return expresultsion.sub('', str(text))



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
            if d.name == "neg" and reviewClassifier(a_new, nbc.training, nbc.positive_mean, nbc.negative_mean) < 0.5:
                correctCount+=1
            elif d.name == "pos" and reviewClassifier(a_new, nbc.training, nbc.positive_mean, nbc.negative_mean) > 0.5:
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
    a_rm = remove_tags(review)
    a_new = a_rm.split(' ')
    words = map(lambda w: tidyWord(w), a_new)
    neg = classify(words, word_list, positive, negative, 0)
    pos = classify(words, word_list, positive, negative, 1)
    relativeFreq = neg / (neg + pos)
    return relativeFreq
# the NBC class 
class NBC:
    def __init__(self, positive_mean, negative_mean, training):
        self.negative_mean = negative_mean
        self.positive_mean = positive_mean
        self.training = training


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
        is_test = True
    if args.classify:
        is_classify = True
    if args.train:
        is_train = True
    
    try:
        directories = pather(path)
    except FileNotFoundError:
        print("Invalid pathname, try again. ")
        sys.exit(0)

    if is_train:
        start = time.time()
        print("Running classification training...")
        nbc = train(directories)
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
        rate = testAllReviews(nbc, directories)
        print("Error rate: {:.2f}%\nTime used: {:.2f}s".format(100 - rate, time.time() - start))

    elif is_classify:
        nbc = load_nbc("nbc.txt")
        print("Skriv inn ditt review:")
        stdin = input()
        start = time.time() 
        result = reviewClassifier(stdin, nbc.training, nbc.positive_mean, nbc.negative_mean)
        if result < 0.5:
            print("The review is negative. Certainty: {:.2f}%".format((1 - result) * 100))
        else:
            print("The review is positive. Certainty: {:.2f}%".format(result * 100))
        print("Time used: {:.2f}s".format(time.time() - start))
        
        
main()
