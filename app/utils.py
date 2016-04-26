from typing import Any, Callable


def convert_in_dict(dct: dict, key: Any, mapper: Callable) -> None:
    dct[key] = mapper(dct[key])
