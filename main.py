import asyncio
from pyppeteer import launch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from bs4 import BeautifulSoup

app = FastAPI()

class LoginRequest(BaseModel):
    email: str
    password: str
    profile_url: str

TEMP_HTML_FILE = "temp.html"

async def save_html_to_file(page, filename):
    # Get the full HTML content of the page
    html_content = await page.content()

    # Save the HTML content to a temp.html file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

async def login_and_scrape_linkedin(email: str, password: str, profile_url: str):
    try:
        # Launch headless Chrome with Pyppeteer
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Set User-Agent to mimic real browser interaction
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # Go to LinkedIn login page
        await page.goto('https://www.linkedin.com/login')
        await page.waitForSelector('input[name="session_key"]')  # Wait for email input

        # Input email and password
        await page.type('input[name="session_key"]', 'prafulk7050@gmail.com', {'delay': 100})  # Type email
        await page.type('input[name="session_password"]', 'Complex#123', {'delay': 100})  # Type password

        # Click the login button
        await page.click('button[type="submit"]')
        await page.waitForNavigation()  # Wait for the page to navigate after login

        # Navigate to the specified LinkedIn profile URL
        await page.goto(profile_url)
        await page.waitForSelector('body')  # Ensure the profile page loads

        # Save the HTML content of the profile page to a file
        await save_html_to_file(page, TEMP_HTML_FILE)

        # Close the browser
        await browser.close()

        # Return a message indicating success
        return {
            "message": f"HTML content saved to {TEMP_HTML_FILE} for the profile: {profile_url}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging in and scraping LinkedIn profile: {str(e)}")

@app.post("/scrape/")
async def scrape_profile(request: LoginRequest):
    # Scrape the LinkedIn profile data after logging in
    result = await login_and_scrape_linkedin(request.email, request.password, request.profile_url)

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

@app.get("/scrape-details/")
async def scrape_details():
    # Check if the temp.html file exists
    if not os.path.exists(TEMP_HTML_FILE):
        raise HTTPException(status_code=404, detail="HTML file not found. Please scrape a profile first.")

    # Read the HTML content
    with open(TEMP_HTML_FILE, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Scrape profile name, headline, and any other public information
    profile_name = soup.find('h1').get_text(strip=True) if soup.find('h1') else 'Not Found'
    headline = soup.find('h2').get_text(strip=True) if soup.find('h2') else 'Not Found'

    return {
        "profile_name": profile_name,
        "headline": headline,
    }

# To run the application, use:
# uvicorn app:app --reload
