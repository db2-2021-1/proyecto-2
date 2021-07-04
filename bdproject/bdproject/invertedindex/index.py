from io import BufferedReader, BufferedWriter
from math import sqrt, log10
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
import json

from os import environ
from pickle import load, dump
from string import punctuation
from typing import List, Set, Dict, overload

import multiprocessing as mp

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
    # Dict[word, Dict[Document, frecuency]]
    index: Dict[str, Dict[str, int]] = {}

    # Dict[document, Dict[word, frecuency]]
    tf: Dict[str, Dict[str, int]] = {}

    # Dict[document, tf_idf_length]
    norms: Dict[str, float] = {}

    n = 0
    while True:
        item = q.get(block=True)
        if item is None:
            norms = {
                id: sqrt(sum([
                    (log10(1.0+f) * log10(float(n)/len(index[w])))**2
                    for w, f in fs.items()
                ]))
                for id, fs in tf.items()
            }
            index_q.put((index, norms, n))
            break

        id: str
        p: Dict[str, int]

        id, p = item
        print(f"Tweet #{n} {id} {len(p)}\r", end="")

        tf[id] = p
        for word, frecuency in p.items():
            index.setdefault(word, {})[id] = frecuency

        n = n+1

class inverse_index(object):
    """Inverse index"""
    def __init__(self):
        self.index: Dict[str, Dict[str, int]] = {}
        self.norms: Dict[str, float] = {}
        self.N: int = 0

    def from_json(self, files: List[str]) -> None:
        j = 8

        pre_q = mp.Queue()
        post_q = mp.Queue()
        index_q = mp.Queue()

        pool = mp.Pool(j, preprocess, (pre_q, post_q,))
        p = mp.Process(target=build_index, args=(post_q, index_q,))

        p.start()

        for file in files:
            with open(file, "r") as r:
                tweets = json.load(r)
                for tweet in tweets:
                    pre_q.put((tweet["id"], tweet["text"]))

        for _ in range(j):
            pre_q.put(None)

        pre_q.close()
        pre_q.join_thread()

        pool.close()
        pool.join()

        post_q.put(None)
        post_q.close()

        self.index, self.norms, self.N = index_q.get()
        print()

    def cos(self,
        Q: Dict[str, float],
        q_n: float,
        V: Dict[str, float],
        v_n: float) -> float:

        return (sum([
            weigth*(V[word] if word in V else 0) for word, weigth in Q.items()
        ]))/(q_n*v_n)

    def df(self, word: str) -> int:
        return len(self.index[word])

    def idf(self, word: str) -> float:
        return log10(float(self.N)/self.df(word))

    def query(self, text:str) -> Dict[str, float]:
        # Dict[word, frecuency]
        q: Dict[str, int] = preprocess_text(text)

        # Dict[document, Dict[word, frecuency]]
        tf: Dict[str, Dict[str, int]] = {}

        union: Set[str] = set()

        for word in q:
            pairs = self.index.get(word)
            if pairs:
                union.add(word)

                for id, f in pairs.items():
                    tf.setdefault(id, {})[word] = f

        # Dict[word, tf_idf]
        q_tf_idf: Dict[str, float] = {
            w: log10(1.0+f)*self.idf(w) for w, f in q.items() if w in union
        }

        q_norm = sqrt(sum([tf_idf**2 for _, tf_idf in q_tf_idf.items()]))

        # Dict[document, Dict[word, tf_idf]]
        tf_idf: Dict[str, Dict[str, float]] = {
            d: {
                w: log10(1.0+f)*self.idf(w) for w, f in fs.items()
            } for d, fs in tf.items()
        }

        # Dict[document, cos]
        cos_ranked: Dict[str, float] = {
            d: self.cos(q_tf_idf, q_norm, v, self.norms[d])
            for d, v in tf_idf.items()
        }


        return dict(
            sorted(
                cos_ranked.items(),
                key=lambda item: item[1], reverse=True
            )
        )

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
            self.index, self.norms, self.N = load(file)


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
            dump((self.index, self.norms, self.N), file)
