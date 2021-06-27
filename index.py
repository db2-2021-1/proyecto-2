#!/usr/bin/env python3

from bdproject.invertedindex.index import index_files
from sys import argv

if __name__ == '__main__':
    index_files(argv[1:])
