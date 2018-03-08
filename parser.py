import os
import glob
import re

#placeholder pathname, kan erstatte med input


path = "placeholder"
savepath = "placeholder"
# åpner alle filer i en path, renser og kopierer til en annen path
for files in glob.glob(path +"*.txt"):
    infile = open(files)
    outfile = open(savepath,'w')
    a = infile.readline().split(' ').toLowerCase().strip(',.-"')
    for k in range (0,len(a)):
        print(a[0], file=outfile, end='')
infile.close()
outfile.close

#for å fjerne html/xml tags med regex, erstatter med mellomrom . Funker med føkka formatering også


def remove_tags(text):
    expression = re.compile(r'<[^>]+>')
    return expression.sub('', text)


