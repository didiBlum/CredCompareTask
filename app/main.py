from fastapi import FastAPI
import asyncio
from app.api.routes import router

app = FastAPI()

app.include_router(router) 