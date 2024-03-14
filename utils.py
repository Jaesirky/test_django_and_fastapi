import json

import anyio
from pathlib import Path
from random import randint

DATA_DIR = Path(__file__).parent.joinpath("data")


def get_fp():
    i = randint(0, 99)
    return DATA_DIR.joinpath(f"{i:004}.json")


async def get_response_async():
    return json.loads(await anyio.Path(get_fp()).read_text())
