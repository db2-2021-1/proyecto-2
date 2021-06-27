from typing import List, Set, Dict
from subprocess import Popen, PIPE
from os import environ
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation

import multiprocessing as mp

file_prefix= "data"
ss = SnowballStemmer("spanish")
stopwords: Set[str] = set(stopwords.words("spanish") + list(punctuation))

def preprocess_text(text: str) -> Dict[str, int]:
    words: List[str] = []

    for token in word_tokenize(text):
        token = token.lower()
        if token not in stopwords:
            words.append(ss.stem(token))

    return dict(zip(words, [words.count(w) for w in words]))

def preprocess(pre_q: mp.Queue, post_q: mp.Queue) -> None:
    while True:
        item = pre_q.get(block=True)
        if item is None:
            break

        id: str
        text: str

        id, text = item
        post_q.put((id, preprocess_text(text)))


def build_index(q: mp.Queue, index_q: mp.Queue) -> None:
    index: Dict[str, Dict[str, int]] = {}
    n = 0
    while True:
        item = q.get(block=True)
        if item is None:
            index_q.put(index)
            break

        id: str
        p: Dict[str, int]

        id, p = item
        print(f"Tweet #{n} {id} {len(p)}\r", end="")
        for word, frecuency in p.items():
            index.setdefault(word, {})[id] = frecuency
        n = n+1

def index_json(files: List[str]) -> Dict[str, Dict[str, int]]:
    environ["PREFIX"] = file_prefix

    printf = Popen(["printf", "%s\\0"]+files, stdout=PIPE)
    tweets = Popen('''
        mkdir -p "$PREFIX"

        function filter-json() {
            jq -cr '.[] | "\\(.id)\\t\\(.text)"' "$@"
        }

        function write-tweets() {
            awk \
                -F'\\t' \\
                -vprefix="$PREFIX" \\
                '{
                    gsub("\\r", " ", $2);
                    printf "%s\\t%s\\n", $1, $2;
                    print $2 > prefix"/"$1;
                }'
        }

        export -f filter-json
        export -f write-tweets

        parallel -0 filter-json |\\
            parallel --pipe --line-buffer write-tweets
    ''', stdin = printf.stdout, stdout=PIPE, text=True, shell=True, executable="bash")

    index: Dict[str, Dict[str, int]] = {}

    if tweets.stdout != None:
        j = 8

        pre_q = mp.Queue()
        post_q = mp.Queue()
        index_q = mp.Queue()

        pool = mp.Pool(j, preprocess, (pre_q, post_q,))
        p = mp.Process(target=build_index, args=(post_q, index_q,))

        p.start()
        for line in tweets.stdout:
            id, text = line[:-1].split('\t')

            pre_q.put((id, text))

        for _ in range(j):
            pre_q.put(None)

        pre_q.close()
        pre_q.join_thread()

        pool.close()
        pool.join()

        post_q.put(None)
        post_q.close()

        #print()

        index = index_q.get()

    return index
