from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

class URLRequest(BaseModel):
    url: str


# To run the application, use:
# uvicorn main:app --reload