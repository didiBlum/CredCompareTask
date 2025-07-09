from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
async def hello_world():
    return {"message": "hello world"} 