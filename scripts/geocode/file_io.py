import json
from typing import *

from marshmallow.utils import EXCLUDE

from schemas import *


def load_streets(paths: List[str]) -> List[Street]:
    existing_streets: Dict[str, Street] = {}
    for path in paths:
        with open(path, encoding="utf-8") as file:
            new_streets: List[Street] = Street.Schema().loads(
                file.read(),
                many=True,
                unknown=EXCLUDE,
            )
            existing_streets |= {f"{s.suburb}_{s.street}": s for s in new_streets}
    streets = list(existing_streets.values())
    if len(paths) > 1:
        save_json("data/streets_merged.json", streets)
    return streets


def save_json(path: str, content: Any):
    with open(path, encoding="utf-8", mode="w+") as file:
        json.dump(
            content,
            file,
            ensure_ascii=False,
            sort_keys=True,
            default=lambda obj: obj.__dict__,
        )
