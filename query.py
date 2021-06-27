#!/usr/bin/env python3

from typing import Dict
from pickle import load
from bdproject.invertedindex.index import stopwords, ss
from sys import argv

if __name__ == '__main__':
    index:  Dict[str, Dict[str, int]] = {}
    with open("index", "rb") as r:
        index = load(r)
    for query in argv[1:]:
        query = query.lower()
        if query not in stopwords:
            print(index[ss.stem(query)])
