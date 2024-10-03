# scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def scrape_linkedin(url):
    options = Options()
    options.add_argument('--headless')  # Run headless Chrome
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Start the Chrome driver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # Check if the page has loaded
        if "Page not found" in driver.page_source:
            return {"error": "Profile not found or inaccessible."}

        # Extract the desired information
        name = driver.find_element(By.CSS_SELECTOR, 'h1.text-heading-xlarge').text
        headline = driver.find_element(By.CSS_SELECTOR, 'div.text-body-medium').text

        data = {
            "name": name,
            "headline": headline,
            "url": url
        }

        return data

    except Exception as e:
        return {"error": str(e)}

    finally:
        driver.quit()

