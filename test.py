import time
import asyncio
from pathlib import Path

from aiohttp import ClientSession
import pandas as pd

DATA_CSV = Path('result').joinpath("data.csv")
DATA_CSV.write_text("app_name,concurrency,total,max,min,mean,rps\n")

HOST = "127.0.0.1"
FASTAPI = "fastapi"
DJANGO = "django"
PORTS = {FASTAPI: 8001, DJANGO: 8002}


async def _request(session, url):
    s = time.time()
    try:
        async with session.get(url) as response:
            await response.read()
            if response.headers["content-type"] != 'application/json':
                return False, 0
    except Exception as _:
        return False, 0
    e = time.time()
    return True, e - s


async def request_app(app_name, loop=10, step=200):
    url = f"http://{HOST}:{PORTS[app_name]}/test"
    f = DATA_CSV.open("a")
    async with ClientSession() as session:
        for l in range(1, loop + 1):
            concurrency = l * step
            mx = 0
            mn = 0
            total = 0
            error = 0
            jobs = [_request(session, url) for _ in range(concurrency)]
            for ok, t in await asyncio.gather(*jobs):
                mx = max(mx, t)
                mn = min(mn, t) if not mn == 0 else t
                total += t
                error += int(not ok)
            rps = concurrency / total
            mean = total / concurrency
            f.write(f"{app_name},{concurrency},{total},{mx},{mn},{mean},{rps}\n")
    f.close()


async def main():
    await request_app(FASTAPI)
    await request_app(DJANGO)


asyncio.run(main())

df = pd.read_csv(DATA_CSV.as_posix())
print(df)
