from typing import List
from subprocess import Popen, PIPE
from os import environ

file_prefix= "data"

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
                '{printf "%s/%s\\n", prefix, $1; print $2 > prefix"/"$1}'
        }

        export -f filter-json
        export -f write-tweets

        parallel -0 filter-json |\\
            parallel --pipe write-tweets
    ''', stdin = printf.stdout, stdout=PIPE, text=True, shell=True, executable="bash")

    if tweets.stdout != None:
        n = 0
        for path in tweets.stdout:
            print(f"Tweet #{n} {path[:-1]}\r", end="")
            n = n+1
        print()
