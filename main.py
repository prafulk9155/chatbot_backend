import asyncio
from pyppeteer import launch
from fastapi import FastAPI, HTTPException
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

    # Validate the URL
    if "linkedin.com" not in profile_url:
        raise HTTPException(status_code=400, detail="Invalid URL. Please provide a valid LinkedIn profile URL.")

    # Scrape the LinkedIn profile data
    scraped_data = await scrape_linkedin_profile(profile_url)

    # Return the scraped data
    return {"scraped_data": scraped_data}

# To run the application, use:
# uvicorn app:app --reload
