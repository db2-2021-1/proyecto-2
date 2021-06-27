#!/usr/bin/env python3

from typing import Dict
from pickle import load
from bdproject.invertedindex.index import query
from sys import argv

if __name__ == '__main__':
    index:  Dict[str, Dict[str, int]] = {}

    with open("index", "rb") as r:
        index = load(r)

    for text in argv[1:]:
        print(query(text, index))
