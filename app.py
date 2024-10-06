import asyncio
from pyppeteer import launch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class URLRequest(BaseModel):
    url: str

async def dismiss_popup(page):
    # Check if a popup appears and close it if it does
    try:
        await page.waitForSelector('.artdeco-modal__actionbar .artdeco-modal__dismiss', timeout=5000)
        await page.click('.artdeco-modal__actionbar .artdeco-modal__dismiss')
    except:
        # If no popup appears, continue
        pass

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

    # Validate the URL
    if "linkedin.com" not in profile_url:
        raise HTTPException(status_code=400, detail="Invalid URL. Please provide a valid LinkedIn profile URL.")

    # Scrape the LinkedIn profile data
    scraped_data = await scrape_linkedin_profile(profile_url)

    # Return the scraped data
    return {"scraped_data": scraped_data}

# To run the application, use:
# uvicorn app:app --reload
