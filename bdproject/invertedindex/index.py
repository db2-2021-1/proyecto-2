from typing import List
from os.path import join

file_prefix = "data"

def tweet2file(id: int, text: str) -> str:
    file_path = join(file_prefix, str(id))

    with open(file_path, "w") as w:
        w.write(text)

    return file_path


def index_json(files: List[str]) -> None:
    for file in files:
        print(file)
