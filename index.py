#!/usr/bin/env python3

from bdproject.invertedindex.index import index_json
from sys import argv

if __name__ == '__main__':
    print(index_json(argv[1:]))
