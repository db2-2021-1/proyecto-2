#!/usr/bin/env python3

from bdproject.invertedindex.index import inverse_index
from sys import argv

if __name__ == '__main__':
    index = inverse_index()
    with open("index", "wb") as w:
        index.from_json(argv[1:])
    index.dump()
