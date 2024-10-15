from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from router.scraper import router as scraprouter
from router.chat import router as chatrouter
from router.upload import router as uploadrouter
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to the Conversational RAG Chatbot API!"}
class URLRequest(BaseModel):
    url: str
app.include_router(scraprouter, prefix="/web")
app.include_router(uploadrouter,prefix="/upload")
app.include_router(chatrouter,prefix="/rag")

# To run the application, use:
# uvicorn main:app --reload