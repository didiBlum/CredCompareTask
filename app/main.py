from fastapi import FastAPI
import asyncio
from app.api.routes import router

app = FastAPI()

@app.get("/")
async def hello_world():
    await asyncio.sleep(0)
    return {"message": "hello world"}

app.include_router(router) 