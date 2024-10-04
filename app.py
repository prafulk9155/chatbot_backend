import asyncio
from pyppeteer import launch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class URLRequest(BaseModel):
    url: str

async def login_to_linkedin(page):
    # Go to LinkedIn login page
    await page.goto('https://www.linkedin.com/login')
    await page.waitForSelector('#username')

    # Fill in the login credentials
    await page.type('#username', 'your_linkedin_email')  # Replace with your LinkedIn email
    await page.type('#password', 'your_linkedin_password')  # Replace with your LinkedIn password

    # Submit the form and wait for navigation
    await page.click('button[type="submit"]')
    await page.waitForNavigation()

async def scrape_linkedin_profile(linkedin_url: str):
    try:
        # Launch headless Chrome with Pyppeteer
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Set User-Agent to mimic real browser interaction
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # Perform login
        await login_to_linkedin(page)

        # Go to the LinkedIn profile URL after logging in
        await page.goto(linkedin_url)
        await page.waitForSelector('h1')  # Wait for the name to appear

        # Scrape name and headline
        name = await page.evaluate('document.querySelector("h1").innerText')
        headline = await page.evaluate('document.querySelector(".text-body-medium").innerText')

        # Close the browser
        await browser.close()

        # Return the scraped profile data
        return {
            "name": name,
            "headline": headline
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
