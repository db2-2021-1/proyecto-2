#!/usr/bin/env python3

from bdproject.bdproject.invertedindex.index import inverse_index
from sys import argv

if __name__ == '__main__':
    index = inverse_index()

    index.load()

    for text in argv[1:]:
        for id in index.query(text):
            print(id)
