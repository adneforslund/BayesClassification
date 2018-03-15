# -*- coding: utf-8 -*-
import codecs
import glob
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="myFile", help="Open specified file")
    args = parser.parse_args()
    myFile = args.myFile

    # This is the one part I added (the read() call)
    text = open(myFile)
    print(text.read())

