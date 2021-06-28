from io import BufferedReader, BufferedWriter
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from os import environ
from pickle import load, dump
from string import punctuation
from subprocess import Popen, PIPE
from typing import List, Set, Dict, overload

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

class inverse_index(object):
    """Inverse index"""
    def __init__(self):
        self.index: Dict[str, Dict[str, int]] = {}

    def from_json(self, files: List[str]) -> None:
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
            ''',
            stdin=printf.stdout,
            stdout=PIPE,
            text=True,
            shell=True,
            executable="bash"
        )

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

            self.index = index_q.get()
            print()

    def query(self, text:str) -> List[str]:
        result: List[str] = []
        seen: set[str] = set()

        q = preprocess_text(text)

        # TODO Cos() tf.idf
        for word in q:
            pairs = self.index.get(word)
            if pairs:
                for id in pairs:
                    if id not in seen:
                        seen.add(id)
                        result.append(id)

        return result

    @overload
    def load(self, file: BufferedReader) -> None: ...

    @overload
    def load(self, file: str) -> None: ...

    @overload
    def load(self) -> None: ...

    def load(self, file = "index") -> None:
        if isinstance(file, str):
            with open(file, "rb") as r:
                self.load(r)
        elif isinstance(file, BufferedReader):
            self.index = load(file)


    @overload
    def dump(self, file: BufferedWriter) -> None: ...

    @overload
    def dump(self, file: str) -> None: ...

    @overload
    def dump(self) -> None: ...

    def dump(self, file = "index") -> None:
        if isinstance(file, str):
            with open(file, "wb") as w:
                self.dump(w)
        elif isinstance(file, BufferedWriter):
            dump(self.index, file)
