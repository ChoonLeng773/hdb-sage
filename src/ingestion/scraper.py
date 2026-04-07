"""
Scrapes HDB pages starting from START_URL and extracts structured content.

The script:
1. Collects links from the main page.
2. Navigates to each child page under Flat, Grant, and Loan Eligibility.
3. Extracts only the relevant HTML content.
4. Saves the scraped data as JSON files in ~/data/raw.

The output is designed to be consumed by a downstream chunking pipeline,
which adds metadata and stores the processed data in a vector database.
"""

import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import Config
from src.ingestion.utils import save_data

# -----------------------------
# Config variables
# -----------------------------
# URLs
BASE_URL = Config.BASE_URL
START_URL = Config.START_URL
# Selectors
NAV_SELECTOR = Config.NAV_SELECTOR
PAGE_LOAD_SELECTOR = Config.PAGE_LOAD_SELECTOR
INFO_SELECTOR = Config.INFO_SELECTOR
# file path
SCRAPER_OUT_DIR = Config.SCRAPER_OUT_DIR


# -----------------------------
# Utility: Selenium helper function
# -----------------------------
def create_driver(headless: bool = False) -> webdriver.Chrome:  # type: ignore
    """
    Creates a Chrome WebDriver instance with headless mode option.

    Args:
        headless (bool): If True, runs Chrome in headless mode. Default is False.

    Returns:
        webdriver.Chrome: An instance of Chrome WebDriver.
    """
    chrome_options = Options()

    # Stealth-ish options
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    if headless:
        # Selenium 4.41+
        chrome_options.add_argument("--headless=new")

    # Initialize ChromeDriver using WebDriver Manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)  # type: ignore

    return driver


# -----------------------------
# Data Extraction Functions
# -----------------------------
def get_childpage_urls(driver) -> list[tuple[str, str]]:
    """
    accepts:
        the selenium webdriver
    returns:
        list of tuples containing the (topic name, url)
    """
    driver.get(START_URL)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGE_LOAD_SELECTOR)))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    sidebar = soup.select_one(NAV_SELECTOR)

    links = []
    if sidebar:
        for a in sidebar.select("li a"):
            text = a.get_text(strip=True)  # the buyer_category
            href = a.get("href")

            if text and href:
                full_url = urljoin(BASE_URL, href)
                links.append((text, full_url))

    return links


def scrape_childpage(driver, buyer_category: str, url: str) -> dict[str, str]:
    """
    Accepts: Driver, topic, url
    Action:
        navigates to the url
        scrapes the data (buyer_category overview, dropdown content)
    Returns:
        category : str of buyers category
        url : web link
        overview : html content
        dropdown : html content (optional)
    """
    print(f"Scraping: {buyer_category}")

    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGE_LOAD_SELECTOR)))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}

    hdb_guide_content = soup.select(INFO_SELECTOR)

    if hdb_guide_content:
        data["data"] = str(hdb_guide_content[0])  # only 1 per page
        data["url"] = url
        data["category"] = buyer_category

    return data


# -----------------------------
# Run pipeline
# -----------------------------


def load_hdb_data():
    """
    Wrapper method for scraping data on HDB Application
    for extension to update vec DB whenever there is a change on HDB's website
    """
    driver = create_driver()

    try:
        links = get_childpage_urls(driver)

        # specifically for this use case, we will have to remove the first link
        unwanted_page_name = "Flat, Grant, and Loan Eligibility"
        parent_page_name = links[0][0]  # assuming not empty

        if parent_page_name == unwanted_page_name:
            del links[0]  # one time operation

        print(f"Found {len(links)} links")

        for buyer_category, url in links:
            # using buyer_category as files name -> there is a slight bug (todo)
            data = scrape_childpage(driver, buyer_category, url)
            save_data(SCRAPER_OUT_DIR, buyer_category, data)
            time.sleep(2)

    finally:
        driver.quit()


def main():
    """
    Main entry point for the HDB data scraping pipeline.

    This function initiates the scraping process by calling load_hdb_data(),
    which scrapes eligibility information from HDB website and saves the target element
    of each page as JSON files under ~/data/raw folder.
    """
    load_hdb_data()


if __name__ == "__main__":
    main()
