from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

from fastapi.middleware.cors import CORSMiddleware
# CORS Configuration
origins = ["http://localhost:3000", "http://127.0.0.1:3000","*"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Initialize the question-answering pipeline with a model
qa_pipeline = pipeline("question-answering")

class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    question: str

# In-memory storage for scraped data
scraped_data_storage = {}

@app.get("/")
async def root():
    return {"message": "Chatbot api working ..."}

@app.post("/scrape/")
async def scrape_website(request: URLRequest):
    try:
        response = requests.get(request.url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        })

        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            scraped_text = " ".join([tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'p'])])

            # Store the scraped text in memory
            scraped_data_storage[request.url] = scraped_text

            # Return the scraped text
            return {"scraped_text": scraped_text, "error":False,"message": "Scraping completed successfully."}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve data from the provided URL.")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_scraped_data(request: QueryRequest):
    # Check if there's scraped data available
    if not scraped_data_storage:
        raise HTTPException(status_code=404, detail="No scraped data available.")

    # Get the last scraped URL
    last_url = list(scraped_data_storage.keys())[-1]
    scraped_text = scraped_data_storage[last_url]

    # Use the question-answering model to get an answer
    answer = qa_pipeline(question=request.question, context=scraped_text)

    return {"answer": answer['answer']}

# To run the application, use:
# uvicorn app:app --reload
