from typing import List, Set
from subprocess import Popen, PIPE
from os import environ
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation

file_prefix= "data"
ss = SnowballStemmer("spanish")
stopwords: Set[str] = set(stopwords.words("spanish") + list(punctuation))

def preprocess(text: str) -> List[str]:
    words: List[str] = []

    for token in word_tokenize(text):
        token = token.lower()
        if token not in stopwords:
            words.append(token)

    return words

def index_json(files: List[str]) -> None:
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

    if tweets.stdout != None:
        n = 0
        for line in tweets.stdout:
            path, text = line[:-1].split('\t')
            print(f"Tweet #{n} {path} {len(preprocess(text))}\r", end="")
            n = n+1
        print()
