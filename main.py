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
    
    print("Loading file contents...")
 
    try:
        dirs = pather(path + "/train")
        vocabulary = set(open(str(path) + "imdb.vocab", encoding='utf-8', errors='ignore').read().splitlines())
    except FileNotFoundError:
        print("Invalid pathname, try again. ")
        sys.exit(0)

    print("Loaded paths and vocabulary from data folder.")
    print("Running training, this may take a while...") 
    number_of_files = 0
    for directory in dirs:
        print("Training from directory: " + directory.name) 
        files = glob.glob(str(directory) + "/*.txt")
        for file in files:
            infile = open(file, encoding='utf-8', errors='ignore')
            line = infile.readline()
            number_of_files+=1
            tokens = split(line)
            for word in tokens:
                if len(word) < 3 or not in_vocabulary(word, vocabulary):
                    continue
                if directory.name == "neg":
                    words_temp.append((word, 0))
                else:
                    words_temp.append((word, 1))

            infile.close()
    print("Numbes of reviews in training set: " + str(number_of_files))
    print("Getting unique words...")
    sys.stdout.flush()
    uniques = set(words_temp)
    
    print("Counting occurences...")
    print("Numbers of unique words in training set: " + str(len(uniques)))
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
# saves nbc.txt during training to be used in classification
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



#
def probability_pre(word, word_list, c):
    if word in word_list:
        (count_in_class, total) = word_list[word]
        if c == 0 and total > 0:
            return float(count_in_class) / float(total)
        elif c == 1 and total > 0:
            return float(total - count_in_class) / float(total)
    return -1.0


def mean(word_class, word_list):
    
    counter = 0
    total = 0
    for w, (i, j) in word_list.items():
        if word_class == 0:
            counter += i
        elif word_class == 1:
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

# takes words from text, removes everything else. 
def split(text):
    expression = re.compile("[\w'|\w]+")
    return expression.findall(str(text))




# iterates through all files in a given path
def pather(path):
    new_path = Path(path)
    directories = [x for x in new_path.iterdir() if x.is_dir() and x.name ==
            "neg" or x.name == "pos"]
    for d in directories:
        print("Path found: {}".format(d))
    sys.stdout.flush()
    return directories

def test_all_reviews(nbc, path):
    try:
        dirs = pather(path + "/test")
    except FileNotFoundError:
        print("Invalid pathname, try again. ")
        sys.exit(0)
    total_count = 0
    correct_count = 0
    
    numbers_of_files_review = 0
    number_of_positive_reviews = 0
    number_of_negative_reviews = 0

    positive_count = 0
    negative_count = 0
    
    for directory in dirs:
        # Apner alle filer i en path,
        print("Testing from directory: " + str(directory))
        for file in glob.glob(str(directory) + "/*.txt"):
            in_file = open(file, encoding='utf-8', errors='ignore')
            line = in_file.readline()
            
            numbers_of_files_review+=1
            classification = review_classifier(line, nbc.training, nbc.positive_mean, nbc.negative_mean)
            
            if directory.name == "neg":
                number_of_negative_reviews+=1
            elif directory.name == "pos":
                number_of_positive_reviews+=1
            
            if classification == -1.0:
                 continue
            elif classification < 0.5:
                negative_count +=1
                if directory.name == "neg":
                    correct_count+=1
                
            elif classification > 0.5:
                positive_count += 1
                if directory.name == "pos":
                    correct_count+=1
                
            total_count+=1

            in_file.close()
    rate = float(correct_count) / float(total_count) * 100
    print("Number of reviews classified: "+str(numbers_of_files_review))
    print("Number of positive reviews in total: "+ str(number_of_positive_reviews) + ". Number of positive classifications: "+str(positive_count) )
    print("Number of negative reviews in total: " + str(number_of_negative_reviews) +
          ". Number of negative classifications: "+str(negative_count))
    print("Number of correct reviews: " + str(correct_count))
    return rate



def review_classifier(review, word_list, positive, negative):
    words = split(review)
    neg = classify(words, word_list, positive, negative, 0)
    pos = classify(words, word_list, positive, negative, 1)
    if neg == -1.0 or pos == -1.0:
       relative_freq = -1.0
    else:
       relative_freq = neg / (neg + pos)
    return relative_freq

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
        rate = test_all_reviews(nbc, path)
        print("Error rate: {:.2f}%\nTime used: {:.2f}s".format(100 - rate, time.time() - start))

    elif is_classify:
        nbc = load_nbc("nbc.txt")
        print("Skriv inn ditt review:")
        stdin = input()
        start = time.time() 
        res = review_classifier(stdin, nbc.training, nbc.positive_mean, nbc.negative_mean)
        print(res)
        if res == -1.0:
            print("The review could not be read, doesn't contain any known words")
        elif res < 0.5:
            print("The review is negative. Certainty: {:.2f}%".format((1 - res) * 100))
        else:
            print("The review is positive. Certainty: {:.2f}%".format(res * 100))
        print("Time used: {:.2f}s".format(time.time() - start))
        
        
main()
