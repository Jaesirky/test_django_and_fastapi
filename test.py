import time
import asyncio
from pathlib import Path

from aiohttp import ClientSession
import pandas as pd

DATA_CSV = Path('result').joinpath("data.csv")

HOST = "192.168.8.83"
FASTAPI = "fastapi"
DJANGO = "django"
PORTS = {FASTAPI: 8001, DJANGO: 8002}

FA_TIME_IMG = Path('result').joinpath("fa_time.jpg")
DJ_TIME_IMG = Path('result').joinpath("dj_time.jpg")
RPS_IMG = Path('result').joinpath("rps.jpg")


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


async def request_app(app_name, loop=20, step=500):
    url = f"http://{HOST}:{PORTS[app_name]}/test"
    f = DATA_CSV.open("a")
    async with ClientSession() as session:
        for l in range(1, loop + 1):
            concurrency = l * step
            accum = 0
            mx = 0
            mn = 0
            error = 0
            jobs = [_request(session, url) for _ in range(concurrency)]
            s = time.time()
            results = await asyncio.gather(*jobs)
            total = time.time() - s
            for ok, t in results:
                mx = max(mx, t)
                mn = min(mn, t) if not mn == 0 else t
                error += int(not ok)
                accum += t
            rps = concurrency / total
            mean = accum / concurrency
            f.write(
                f"{app_name},{concurrency},{total},{mx},{mn},{mean},{rps},{error}\n"
            )
    f.close()


async def main():
    DATA_CSV.write_text("app_name,concurrency,total,max,min,mean,rps,error\n")
    await request_app(FASTAPI)
    await request_app(DJANGO)


s = time.time()
asyncio.run(main())
print(time.time() - s)

FIG_SIZE = (12, 8)

# 统计
df_result = pd.read_csv(DATA_CSV.as_posix())
print(df_result)
print("RPS:", df_result["rps"].mean())

df_result_concurrent_index = df_result.set_index(["app_name", "concurrency"])
print(df_result_concurrent_index)
df_result_concurrent_index.loc[FASTAPI][["max", "min", "mean", "total"]].plot(
    figsize=FIG_SIZE,
    xticks=df_result["concurrency"]).get_figure().savefig(FA_TIME_IMG)
df_result_concurrent_index.loc[DJANGO][["max", "min", "mean", "total"]].plot(
    figsize=FIG_SIZE,
    xticks=df_result["concurrency"]).get_figure().savefig(DJ_TIME_IMG)
df_result[["app_name", "concurrency",
           "rps"]].set_index(["concurrency", "app_name"]).unstack().plot(
               figsize=FIG_SIZE,
               xticks=df_result["concurrency"]).get_figure().savefig(RPS_IMG)
