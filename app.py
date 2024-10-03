from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

class URLRequest(BaseModel):
    url: str

@app.post("/scrape/")
async def scrape_website(request: URLRequest):
    try:
        response = requests.get(request.url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        })

        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            scraped_data = {}

            # Scrape headings and paragraphs
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
                scraped_data[tag.name] = scraped_data.get(tag.name, []) + [tag.get_text(strip=True)]

            # Scrape divs
            for div in soup.find_all('div'):
                div_text = div.get_text(strip=True)
                if div_text:
                    scraped_data['div'] = scraped_data.get('div', []) + [div_text]

            # Return the scraped data
            return {"scraped_data": scraped_data}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve data from the provided URL.")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run the application, use:
# uvicorn app:app --reload
