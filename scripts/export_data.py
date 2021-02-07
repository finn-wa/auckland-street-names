import json
from glob import glob
from itertools import chain
from typing import *


def load_data(path: str) -> List[Any]:
    with open(path, encoding="utf-8") as file:
        return json.loads(file.read())


paths = glob("data/geocoded/*json")
streets = list(chain.from_iterable(load_data(p) for p in paths if "unmatched" not in p))

with open("docs/data.js", mode="a+", encoding="utf-8") as outfile:
    outfile.write("const streetData = ")
    json.dump(streets, outfile, ensure_ascii=False, separators=(",", ":"))
