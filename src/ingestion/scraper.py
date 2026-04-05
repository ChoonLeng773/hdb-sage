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

import json
import re
import time

from urllib.parse import urljoin
from pathlib import Path
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

# -----------------------------
# Config variables
# -----------------------------

# To segment out this portion onto a config file

# URLs
BASE_URL = "https://www.hdb.gov.sg"
START_URL = "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/application-for-an-hdb-flat-eligibility-hfe-letter"

# -----------------------------
# Selectors -> once developed, move into config file
# -----------------------------
# get_childpage_urls
NAV_SELECTOR = "nav.PSidebar.DestinationLayout_DestinationPageLayout__PSidebar__Z_Yym"
# scrape data
PAGE_LOAD_SELECTOR = "img.hdb__logo"
# (0, n) within each child page -> move these variables into the chunker
CAT_SELECTOR = "div.accordion-header"
DATA_SELECTOR = "div.AccordionWrapper_accordionCollapse__wyfTM"

OVERVIEW_SELECTOR = "div.BodyContent_BodyContent__xr2hZ"
DROPDOWN_SELECTOR = (
    "div.PAccordion accordion accordion-flush AccordionWrapper_Accordion__ywOd_"
)


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

    overview_content = soup.select(OVERVIEW_SELECTOR)
    dropdown_content = soup.select(DROPDOWN_SELECTOR)

    if overview_content:
        data["overview"] = overview_content[0].get_text(strip=True)  # must only have 1
        data["url"] = url  # only include if overview is found
        data["category"] = buyer_category
    if dropdown_content:
        data["dropdown"] = dropdown_content[0].get_text(
            strip=True
        )  # should only have 1 container

    return data


# -----------------------------
# Save Function
# -----------------------------
def sanitize_filename(name: str) -> str:
    """
    Lowers casing for file naming
    Removes weird characters which can cause issues for saving the file
    replaces spacing with underscore
    """
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s]+", "_", name)
    return name


def save_json(title: str, data: dict[str, str]):
    """
    Takes the name of the section as well as the dictionary
    Creates the json file containing {subsections : html}
    Saved to ~/data/raw to be chunked
    """
    filename = sanitize_filename(title) + ".json"
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved: {filename}")  # filepath to check


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
            data = scrape_childpage(driver, buyer_category, url)
            save_json(buyer_category, data)
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
