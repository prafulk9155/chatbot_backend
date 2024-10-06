import asyncio
from pyppeteer import launch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

class URLRequest(BaseModel):
    url: str

async def set_linkedin_cookies(page):
    # Add your cookies (from the browser's dev tools) here
    cookies = [
        {
            "name": "li_at",
            "value": "AQEDAVOUOWsAv-XsAAABkmKb00kAAAGShqhXSVYABhInaI58G-FyjXIELWsRy1r1S2OV1Jz_LT8q9H5lykD16MXXOwv7s1PkB57pYRDE9kHTOlmhEZDpcdgXFZMH0giuwlupg0dft8OSKFRhHKIwaqMh",  # Replace with your cookie value
            "domain": ".linkedin.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        },
        {
            "name": "JSESSIONID",
            "value": "ajax:1597530069556966703",  # Replace with your cookie value
            "domain": ".linkedin.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        },
        # Add other relevant cookies here if necessary
    ]
    
    # Set cookies in the browser
    await page.setCookie(*cookies)

async def scrape_linkedin_profile(linkedin_url: str):
    try:
        # Launch headless Chrome with Pyppeteer
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Set User-Agent to mimic real browser interaction
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # Set the cookies for LinkedIn from your logged-in session
        await set_linkedin_cookies(page)

        # Go directly to the LinkedIn profile URL
        await page.goto(linkedin_url)
        await page.waitForSelector('h1', 'p','span')  # Wait for the page to load

        # Scrape all the visible text content from the page
        page_content = await page.evaluate('''() => {
            return document.body.innerText;
        }''')

        # Close the browser
        await browser.close()

        # Return the scraped page content for analysis
        return {
            "page_content": page_content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping LinkedIn profile: {str(e)}")

@app.post("/scrape/")
async def scrape_profile(request: URLRequest):
    profile_url = request.url

<<<<<<< HEAD
        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            scraped_text = " ".join([tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'li'])])
=======
    # Validate the URL
    if "linkedin.com" not in profile_url:
        raise HTTPException(status_code=400, detail="Invalid URL. Please provide a valid LinkedIn profile URL.")
>>>>>>> fdee43c (some code added for testing)

    # Scrape the LinkedIn profile data
    scraped_data = await scrape_linkedin_profile(profile_url)

<<<<<<< HEAD
            # Return the scraped text
            return {"error": False, "scraped_text": scraped_text}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve data from the provided URL.")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize the text generation model
llm_pipeline = pipeline("text-generation", model="gpt2")  # or "EleutherAI/gpt-neo-125M"

def get_llm_answer(scraped_text, question):
    prompt = f"Here is some information about a website:\n\n{scraped_text}\n\nGiven this information, answer the following question:\n{question}\n\nAnswer:"
    
    # Limit the length of the prompt to avoid index errors
    if len(prompt) > 1024:
        prompt = prompt[:1024]
        print(prompt)  # Truncate the prompt to the first 1024 characters

    # Use the local model for generation with adjusted parameters
    response = llm_pipeline(prompt, max_new_tokens=50, num_return_sequences=1)  # Adjust max_new_tokens as needed

    return response[0]['generated_text'].strip()

@app.post("/query/")
async def query_scraped_data(request: QueryRequest):
    if not scraped_data_storage:
        raise HTTPException(status_code=404, detail="No scraped data available.")

    last_url = list(scraped_data_storage.keys())[-1]
    scraped_text = scraped_data_storage[last_url]

    answer = get_llm_answer(scraped_text, request.question)

    return {
        "error": False,
        "answer": answer,
        "context": scraped_text[:100]  # Optionally, return a snippet of the context
    }
=======
    # Return the scraped data
    return {"scraped_data": scraped_data}
>>>>>>> fdee43c (some code added for testing)

# To run the application, use:
# uvicorn app:app --reload
