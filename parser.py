import os
import glob
import re

#placeholder pathname, kan erstatte med input
# kanskje ikke så lurt å gjøre om hele settet hver gang

path = "placeholder"
savepath = "placeholder"
for files in glob.glob(path +"*.txt"):
    infile = open(files)
    outfile = open(savepath,'w')
    a = infile.readline().split(' ').toLowerCase().strip(',.-"')
    for k in range (0,len(a)):
        print(a[0], file=outfile, end='')
infile.close()
outfile.close

#for å fjerne html tags med regex, kan muligens bruke XML fra pythons standard-bibliotek til dette. Funker med føkka formatering også
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

#fikk ikk den til å funke
#def remove_tags(text):
#    ''.join(xml.etree.ElementTree.fromstring(text).itertext())
