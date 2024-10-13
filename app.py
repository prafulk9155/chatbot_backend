import asyncio
from pyppeteer import launch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

class URLRequest(BaseModel):
    url: str

TEMP_HTML_FILE = "temp.html"

async def dismiss_popup(page):
    # Check if a popup appears and close it if it does
    try:
        await page.waitForSelector('.artdeco-modal__actionbar .artdeco-modal__dismiss', timeout=5000)
        await page.click('.artdeco-modal__actionbar .artdeco-modal__dismiss')
    except:
        # If no popup appears, continue
        pass

async def save_html_to_file(page, filename):
    # Get the full HTML content of the page
    html_content = await page.content()

    # Save the HTML content to a temp.html file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

async def scrape_linkedin_profile(linkedin_url: str):
    try:
        # Launch headless Chrome with Pyppeteer
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Set User-Agent to mimic real browser interaction
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # Go to the LinkedIn profile URL
        await page.goto(linkedin_url)
        await page.waitForSelector('body')  # Ensure the page loads

        # Dismiss any popups if they appear
        await dismiss_popup(page)

        # Save the HTML content of the page to a file
        await save_html_to_file(page, TEMP_HTML_FILE)

        # Close the browser
        await browser.close()

        # Return a message indicating success
        return {
            "message": f"HTML content saved to {TEMP_HTML_FILE}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping LinkedIn profile: {str(e)}")

@app.post("/scrape/")
async def scrape_profile(request: URLRequest):
    profile_url = request.url

    # Validate the URL
    if "linkedin.com" not in profile_url:
        raise HTTPException(status_code=400, detail="Invalid URL. Please provide a valid LinkedIn profile URL.")

    # Scrape the LinkedIn profile data and save HTML to temp.html
    result = await scrape_linkedin_profile(profile_url)

    # Return the result
    return result

@app.get("/html/")
async def get_html_file():
    # Check if the temp.html file exists
    if not os.path.exists(TEMP_HTML_FILE):
        raise HTTPException(status_code=404, detail="HTML file not found. Please scrape a profile first.")

    # Read and return the HTML content from temp.html
    with open(TEMP_HTML_FILE, "r", encoding="utf-8") as file:
        html_content = file.read()

    return {"html_content": html_content}

# To run the application, use:
# uvicorn app:app --reload
