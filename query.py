#!/usr/bin/env python3

from bdproject.invertedindex.index import inverse_index
from sys import argv

if __name__ == '__main__':
    index = inverse_index()

    with open("index", "rb") as r:
        index.load(r)

    for text in argv[1:]:
        print(index.query(text))
