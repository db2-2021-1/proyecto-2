#!/usr/bin/env python3

from pickle import dump
from bdproject.invertedindex.index import index_json
from sys import argv

if __name__ == '__main__':
    with open("index", "wb") as w:
        dump(index_json(argv[1:]), w)
