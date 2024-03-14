from fastapi import FastAPI

from utils import get_response_async

app = FastAPI()


@app.get("/test")
async def test():
    return await get_response_async()
