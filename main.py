from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from router.scraper import router as scraprouter
app = FastAPI()

class URLRequest(BaseModel):
    url: str
app.include_router(scraprouter, prefix="/web")

# To run the application, use:
# uvicorn main:app --reload