# -*- coding: utf-8 -*-
import sys
import codecs
if sys.stdout.encoding != 'cp850':
  sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'cp850':
  sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'strict')

import os
import glob
import re
import time

from pathlib import Path

negativeMean = 0
positiveMean = 0

path = Path('DATA/aclImdb/train/')
dirs = [x for x in path.iterdir() if x.is_dir() and x.name == "neg" or x.name == "pos"]
for d in dirs:
    print(d)



# Words blir en liste med tuples (word, 0) eller (word, 1), hvor 0 er negativ og 1 er positiv 
words = []

def probabilityPre(word, wordlist, c):
    classCounter = 0
    wordCounter = 0
    for(w, cl) in wordlist:
        if w == word and c == cl:
            classCounter += 1
        if w == word:
            wordCounter += 1
    if wordCounter > 0:
        return float(classCounter) / float(wordCounter)
    else:
        return -1.0

def mean(clas, wordlist):
    counter = 0
    for (w, c) in wordlist:
        if c == clas:
            counter += 1
    return float(counter) / float(len(wordlist))


def bayes(a, b, pre):
    return (a*pre)/b

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

#for Ã¥ fjerne html/xml tags med regex, erstatter med mellomrom . Funker med fÃ¸kka formatering ogsÃ¥
def remove_tags(text):
    expression = re.compile(r'<[^>]+>')
    return expression.sub('', text)


def remove_punctuation(text):
    for p in [',', '!', '"', '.', '?', ')', '(', '-', "'s"]:
        text = text.replace(p, '')
    return text


def reviewClassifier(review,wordlist, c):
    a_rm = remove_tags(review)
    a_new = a_rm.split(' ')
    sum = 0
    total = len(a_new)
    current = 0
    for word in a_new:
        current += 1
        loading = (current / total) * 100
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" + str(int(loading)) + "%")
        word = word.lower()
        word = remove_punctuation(word)
        prob = classify(word, wordlist, c)
        if  prob != -1.0:
            sum += prob
        else:
            continue
    return sum / len(a_new)
    
        


for d in dirs:
    # Ã¥pner alle filer i en path, renser og kopierer til en annen path
    for file in glob.glob(str(d) + "/*.txt"):
        # print(file)            
        infile = open(file, encoding='utf-8', errors='ignore')
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

testReview = "The Detonator is set in Bucharest where some sort of ex CIA Government agent named Sonni Griffith (Wesley Snipes) has tracked down a arms dealer named Dimitru (Matthew Leitch), things go wrong though & Dimitru finds out that Sonni is working for the US Government. After a big shoot-out most of Dimitru's men have been killed by Sonni which the local Romanian police force are unhappy about, top man Flint (Michael Brandon) decides to send Sonni back to the US & at the same time protect a woman named Nadia Cominski (Silvia Colloca) who is also being sent back to the US. However it turns out that Nadia is wanted by Dimitru & his football club owning boss Jozef (Tim Dutton) who need her in order to complete a deal for a nerve gas bomb which they intend to set off in Washington killing millions of people...<br /><br />This American & Romanian co-production was directed by Po-Chih Leong & The Detonator confirms beyond any shadow of a doubt that Wesely Snipes has joined the washed up action film stars club who are relegated to making generic action films in Eastern European locations, yep Snipes has joined such luminaries as Jean-Claude Van Damme, Steven Seagal, Dolph Lundgren, Rutger Hauer & Chuck Norris. I give Snipes a bit of credit since he held on a little longer than the rest with the excellent Blade: Trinity (2004) still fresh in a lot of cinema goers minds (every film he has made since has gone straight-to-DVD) but it had to happen sooner or later, like a lot of the names I've mentioned Snipes has lived off the reputation of a few great films & if you look at his career he's been in more bad films that good ones. Like the recent films of JCVD & Seagal The Detonator is pretty awful. The script by Martin Wheeler is as predictable, boring & by-the-numbers as anything out there. The Detonator is the sort of film you expect to see on an obscure cable TV channel playing at 2 O'clock in the morning. The Detonator is chock full of clichÃ©s, Snipes is forced into a situation where he has to protect a woman & at first they dislike each other but by the end they are in love, his closest friend at the CIA turns out to be a traitor while the obnoxious by the book boss no-one likes actually turns out to be a pretty decent guy, Snipes character is allowed to run around Bucharest shooting, killing & blowing people up like it doesn't matter & he never gets arrested, the action is dull & forgettable, the bad guy own a football club so there are lots of annoying football terminology & there aren't even any funny one-liners.<br /><br />Director Leong doesn't do anything anything to liven things up, The Detonator looks cheap with a car chase in which the two cars never seem to get over the 30mph mark. OK the action scenes are relatively well staged but they are few & far between & utterly forgettable in a 'bad guy shoots at Snipes & misses, in return Snipes shoots at bad guy & kills him' sort of way. There's a half decent car crash & explosion but very little else. It seems some of The Detonator was shot in a Romanian football stadium, I think I'd rather have watched the game for 90 minutes rather than this film.<br /><br />With a supposed budget of about $15,000,000 The Detonator is reasonably well made but not that much really happens. Set & filmed in Bucharest in Romania. The acting isn't that great, Snipes just doesn't seem interested & feels like he is just there for the money which I don't blame him for at all.<br /><br />The Detonator is yet another poor clichÃ©d action film starring a has been actor & set in Eastern Europe. Why do Sony keep making these things? Not recommend, there are much better action fare out there."


positiveMean = mean(1, words)
negativeMean = mean(0, words)
start = time.time()
print("negative review chance: "+str(reviewClassifier(testReview,words, 0)))
print("kjÃ¸retid : " + str(time.time() - start))
