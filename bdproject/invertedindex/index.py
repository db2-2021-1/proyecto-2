from typing import List, Set, Dict
from subprocess import Popen, PIPE
from os import environ, path
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation

file_prefix= "data"
ss = SnowballStemmer("spanish")
stopwords: Set[str] = set(stopwords.words("spanish") + list(punctuation))

def preprocess(text: str) -> Dict[str, int]:
    words: List[str] = []

    for token in word_tokenize(text):
        token = token.lower()
        if token not in stopwords:
            words.append(token)

    return dict(zip(words, [words.count(w) for w in words]))

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
                    printf "%s/%s\\t%s\\n", prefix, $1, $2;
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
        n = 0
        for line in tweets.stdout:
            path, text = line[:-1].split('\t')

            print(f"Tweet #{n} {path}\r", end="")
            index[path.split('/')[-1]] = preprocess(text)

            n = n+1
        print()

    return index
