#!/usr/bin/env python3

from bdproject.invertedindex.index import inverse_index, file_prefix
from os.path import join
from sys import argv

if __name__ == '__main__':
    index = inverse_index()

    index.load()

    for text in argv[1:]:
        for id in index.query(text):
            print(join(file_prefix, id))
