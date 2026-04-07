import os
import re
import json
import uuid

from typing import Callable
from pathlib import Path
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from config import Config


CAT_SELECTOR = Config.CAT_SELECTOR
DATA_SELECTOR = Config.DATA_SELECTOR
# these two
OVERVIEW_SELECTOR = Config.OVERVIEW_SELECTOR
SUBSECTION_SELECTOR = "div.accordion-item.m-0"


# -------------------------------------------------------------------------------------------------
# Methods dealing with JSON data
# -------------------------------------------------------------------------------------------------
def get_raw_data(raw_data_dir: Path) -> list[dict[str, str]]:
    """
    accepts: string input path (project_root = Path(__file__).resolve().parents[2])
    returns: list of dict mirroring json data found in raw data directory
    """
    results: list[dict[str, str]] = []

    for file_path in raw_data_dir.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # validate bad json files
            if not all(k in data for k in ("data", "url", "category")):
                print(f"[SKIP] Missing keys in {file_path.name}")
                continue

            results.append(data)

        except Exception as e:
            print(f"[ERROR] {file_path.name}: {e}")

    return results


def test_get_raw_data() -> dict[str, str]:
    """
    accepts, returns : None
    Actions: prints one json data, and string to notify if raw data fetch has passed.
    raises error if data formatting does not fit definition.
    """
    project_root = Path(__file__).resolve().parents[2]
    data_directory = project_root / "data" / "raw"
    data_file_list = get_raw_data(data_directory)

    assert isinstance(data_file_list, list)
    assert len(data_file_list) > 0

    # validate json data. (move to config if time permits)
    sample = data_file_list[0]
    assert "data" in sample
    assert "url" in sample
    assert "category" in sample

    # print(sample)
    print("test_get_raw_data passed")
    return sample


# test_get_raw_data()


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


def save_data(chunk_id: str, category: str, data: dict[str, str]):
    """
    Takes the name of the section as well as the dictionary
    Creates the json file containing {subsections : html}
    Saved to ~/data/raw to be chunked
    """
    filename = sanitize_filename(f"{chunk_id}_{category}") + ".json"
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "data" / "chunks"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:  # overwrites existing files
        json.dump(data, f, indent=2, ensure_ascii=False)


# def save_data(output_dir: str, file_name: str):
#     # Save to processed directory with same filename
#     output_file = output_dir / file_name
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(output_data, f, ensure_ascii=False, indent=2)

#     print(f"[OK] Processed {file_path.name}")


# -------------------------------------------------------------------------------------------------
# Process HTML according to sections [brief overview, accordion extra info thingy]
# -------------------------------------------------------------------------------------------------
def process_html(html: str, chunk_function: Callable[[str], list[str]]) -> list[str]:
    """
    Goes through the HTML string and separates them into sections
    - overview section of the page (div body content)
    - dropdown subsections within each page (div accordion-item)
    calls a table check (has_table), flattens tables into meaningful text
    within each section, it calls chunk_text to further reduce the size of the chunk if necessary
    """
    soup = BeautifulSoup(html, "html.parser")
    overview_elements = soup.select(OVERVIEW_SELECTOR)
    subsec_elements = soup.select(SUBSECTION_SELECTOR)
    elements = []  # add these as you select them
    if overview_elements:
        elements.extend(overview_elements)
    if subsec_elements:
        elements.extend(subsec_elements)

    # chunk_text() -> handle the chunking of each section
    chunks = []
    for el in elements:
        # each subsection should have different kinds of information about the main topic
        text_data = html_to_text(str(el))
        chunks.extend(chunk_function(text_data))

    return chunks


def html_to_text(html: str) -> str:
    """
    Headings (h1-h6) → markdown hashtags to be included for structure
    Paragraphs → plain text
    Lists → bullet points
    Tables → row-wise structured text
    Ignore non-text elements (img, iframe, etc.)
    """
    soup = BeautifulSoup(html, "html.parser")

    def clean_text(text):
        return " ".join(text.split())

    def parse_table(table: Tag) -> str:
        rows = []

        # Extract headers
        headers = []
        thead = table.find("thead")
        if thead:
            headers = [clean_text(th.get_text()) for th in thead.find_all("th")]

        # Extract rows
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            values = [clean_text(td.get_text()) for td in cells]

            # Skip header row if already captured
            if headers and values == headers:
                continue

            if headers and len(headers) == len(values):
                row_text = " | ".join(
                    f"{headers[i]}: {values[i]}" for i in range(len(values))
                )
            else:
                row_text = " | ".join(values)

            if row_text:
                rows.append(row_text)

        return "\n".join(rows)

    def parse_node(node, level=0) -> str:
        result = []

        if isinstance(node, NavigableString):
            text = clean_text(str(node))
            return text if text else ""

        if not isinstance(node, Tag):
            return ""

        name = node.name.lower()

        # Skip irrelevant tags
        if name in ["script", "style", "img", "iframe"]:
            return ""

        # Headings -> markdown
        if name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            text = clean_text(node.get_text())
            if text:
                return f"\n{'#' * int(name[1])} {text}\n"

        # Paragraph
        if name == "p":
            text = clean_text(node.get_text())
            return f"{text}\n" if text else ""

        # Lists
        if name in ["ul", "ol"]:
            for li in node.find_all("li", recursive=False):
                li_text = parse_node(li, level + 1)
                if li_text.strip():
                    result.append(f"{'  '*level}- {li_text.strip()}")
            return "\n".join(result) + "\n"

        if name == "li":
            return clean_text(node.get_text())

        # Tables
        if name == "table":
            return "\n" + parse_table(node) + "\n"

        # Default: recurse into children
        for child in node.children:
            child_text = parse_node(child, level)
            if child_text:
                result.append(child_text)

        return "".join(result)

    return parse_node(soup).strip()


# specifically for testing process_html
# data = test_get_raw_data()
# html_data = data["data"]
# clean_string = html_to_text(html_data)
# print(clean_string)
# honestly, this function works like a dream :() now we just need to separate the top and bottom


# -------------------------------------------------------------------------------------------------
# Chunk data
# -------------------------------------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = 256, overlap: int = 50) -> list[str]:
    """
    Splits text into overlapping chunks.
    """
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]  # slice handles out-of-range
        chunks.append(" ".join(chunk))
        start += chunk_size - overlap

    return chunks


# -------------------------------------------------------------------------------------------------
# Wrapper function to bring everything together
# -------------------------------------------------------------------------------------------------
def generate_chunks() -> list[dict[str, str]]:
    """
    looks through ~/data/raw to find the json files output from scraper.py
    generates chunks with metadata {define the metadata here :) }
    """
    prefix = "dc"  # data chunk
    chunk_counter = 1
    project_root = Path(__file__).resolve().parents[2]
    data_directory = project_root / "data" / "raw"
    website_pages = get_raw_data(data_directory)
    for page_dict in website_pages:
        html_data = page_dict["data"]
        url = page_dict["url"]
        cat = page_dict["category"]
        chunks = process_html(html_data, chunk_text)
        metadata_chunks = []
        # able to split category into main and sub categories here
        for chunk in chunks:
            chunk_id = f"{prefix}_{chunk_counter:04d}"
            print("chunk_id" + " : " + chunk)
            chunk_counter += 1
            output_data = {
                "url": url,
                "category": cat,
                "data": chunk,
                "chunk_id": chunk_id,
            }
            # Save function to review
            save_data(chunk_id, cat, output_data)
            metadata_chunks.append(output_data)
    return metadata_chunks


# -------------------------------------------------------------------------------------------------
# main method
# -------------------------------------------------------------------------------------------------
def main():
    """
    Main entry point for the HDB data scraping pipeline.

    This function initiates the scraping process by calling load_hdb_data(),
    which scrapes eligibility information from HDB website and saves the target element
    of each page as JSON files under ~/data/raw folder.
    """
    generate_chunks()


if __name__ == "__main__":
    main()
