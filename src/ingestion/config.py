"""
Configuration definitions for the ingestion service.

Encapsulates all static parameters required for:
- Web navigation (URLs)
- HTML parsing (CSS selectors)

To be used for scraper and chunker
"""


class IngestionConfig:
    """
    Static configuration constants for the ingestion stage.
    """

    # URLs
    BASE_URL = "https://www.hdb.gov.sg"
    START_URL = "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/application-for-an-hdb-flat-eligibility-hfe-letter"
    # Scraping Selectors
    NAV_SELECTOR = (
        "nav.PSidebar.DestinationLayout_DestinationPageLayout__PSidebar__Z_Yym"
    )
    PAGE_LOAD_SELECTOR = "img.hdb__logo"
    INFO_SELECTOR = "div.DestinationLayout_DestinationPageLayout__Cont__5NdTz.col-md-8.col-sm-12.offset-md-1"  # parent selector

    OVERVIEW_SELECTOR = "div.BodyContent_BodyContent__xr2hZ"
    DROPDOWN_SELECTOR = (
        "div.PAccordion.accordion.accordion-flush.AccordionWrapper_Accordion__ywOd_"
    )
    # Chunking Selectors
    CAT_SELECTOR = "div.accordion-header"  # (0, n) within each child page
    DATA_SELECTOR = "div.AccordionWrapper_accordionCollapse__wyfTM"
    SUBSECTION_SELECTOR = "div.accordion-item.m-0"
    # Directory Vectors
    CHUNKER_OUT_DIR = "data/chunks"
    SCRAPER_OUT_DIR = "data/raw"
