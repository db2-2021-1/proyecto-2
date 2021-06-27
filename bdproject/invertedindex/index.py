import json_stream

from typing import List
from os.path import join
from subprocess import Popen, PIPE
from pathlib import Path

file_prefix= "data"

def tweet2file(id: int, text: str) -> str:
    file_path = join(file_prefix, str(id))

    with open(file_path, "w") as w:
        w.write(text)

    return file_path


def index_json(files: List[str]) -> None:
    Path(file_prefix).mkdir(parents=True, exist_ok=True)

    args = Popen(["printf", "%s\\0"] + files, stdin=PIPE, stdout=PIPE)
    jq = Popen(["parallel", "-0", "jq '.[] | {id, text}'"], stdin=args.stdout, stdout=PIPE, text=True)

    if args.stdout != None:
        args.stdout.close()

    tweets = 0
    try:
        while True:
            data = json_stream.load(jq.stdout)
            tweet2file(data["id"], data["text"])

            print(f"Tweets: {tweets}\r", end='')
            tweets = tweets + 1
            data.read_all()


    except StopIteration:
        print()

