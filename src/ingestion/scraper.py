import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import re
import time
from pathlib import Path

# To segment out this portion onto a config file
BASE_URL = "https://www.hdb.gov.sg"
START_URL = "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/application-for-an-hdb-flat-eligibility-hfe-letter"

# can be any mainstream browsers
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# -----------------------------
# Utility: clean filename || might not be necessary given our sample data
# -----------------------------
def sanitize_filename(name: str) -> str:
    '''
    Lowers casing for file naming
    Removes weird characters which can cause issues for saving the file
    replaces spacing with underscore
    '''
    name = name.strip().lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s]+', '_', name)
    return name


# -----------------------------
# Step 1: Extract sidebar links
# -----------------------------
def get_sidebar_links():
    response = requests.get(START_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    sidebar = soup.select_one(
        "div.DestinationLayout_DestinationPageLayout__SidebarCont__BeKWW nav.PSidebar"
    )

    print(sidebar)

    links = []

    if sidebar:
        for a in sidebar.select("ul a"):
            text = a.get_text(strip=True)
            href = a.get("href")

            if href:
                full_url = urljoin(BASE_URL, href)
                links.append((text, full_url))

    return links


# -----------------------------
# Step 2: Scrape each page
# -----------------------------
def scrape_page(title, url):
    print(f"Scraping: {title}")

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    data = {}

    accordion_items = soup.select("div.accordion-item.m-0")

    for item in accordion_items:
        # Extract heading
        header = item.select_one("div.h5.mb-3")

        if header:
            key = header.get_text(strip=True)
        else:
            key = "unknown_section"

        # Store full HTML
        data[key] = str(item)

    return data


# -----------------------------
# Step 3: Save to JSON
# -----------------------------
def save_json(title, data):
    '''
    Takes the name of the section as well as the dictionary
    Creates the json file containing {subsections : html}
    Saved to ~/data/raw to be chunked
    '''
    filename = sanitize_filename(title) + ".json"
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved: {filepath}")


def reload_hdb_data():
    '''
    Wrapper method for scraping data on HDB Application
    '''
    links = get_sidebar_links()
    print(f"Scraping {len(links)} links")

    for text, url in links:
        try:
            data = scrape_page(text, url)
            save_json(text, data)
            # for windows
            time.sleep(1)

        except Exception as e:
            print(f"Error processing {text}: {e}")

# -----------------------------
# Run pipeline
# -----------------------------
def main():
    reload_hdb_data()


if __name__ == "__main__":
    main()