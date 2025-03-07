import logging
import multiprocessing
import re
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from typing import Tuple
import datetime

# Configure logging (writes to both console and file)
LOG_FILE = "scraper.log"
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler(LOG_FILE, mode="a"),  # Log file output
    ],
)


def _search_str_property(listing):
    size_match = re.search(r"(\d+\s*m2)", listing)
    size = size_match.group(1) if size_match else None
    type_match = re.search(r"\b(apartment|house|room)\b", listing, re.IGNORECASE)
    property_type = type_match.group(1) if type_match else None
    location_match = re.search(r"(?<=\bin\s)(.*)", listing)
    location = location_match.group(1).strip() if location_match else None
    return size, property_type, location


def parse_listing_html(li_element) -> Tuple[str, int]:
    bs4_html = BeautifulSoup(li_element.get_attribute("outerHTML"), "html.parser")
    link = bs4_html.find("a")["href"]
    rent = bs4_html.find("label").parent.find("span").text
    size, property_type, location = _search_str_property(bs4_html.find("a").text)
    return link, rent, size, property_type, location


def _get_chrome_driver(headless=True):
    """Get Chrome WebDriver with suppressed logging."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Suppress logs
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # os.environ["WDM_LOG_LEVEL"] = "0"  # Disable WebDriver logs
    # os.environ["WDM_PRINT_FIRST_LINE"] = "False"

    return webdriver.Chrome(options=chrome_options)


def get_listings(url, visited, final, base_url="https://www.housingtarget.com"):
    if url in visited:
        return
    logging.info(f"Visiting {url}")
    visited.add(url)
    driver = _get_chrome_driver()
    driver.get(url)

    ul_element = driver.find_element(By.CLASS_NAME, "table-ads")
    li_elements = ul_element.find_elements(By.TAG_NAME, "li")
    listings = [
        li
        for li in li_elements
        if li.get_attribute("class") == "" and li.find_elements(By.TAG_NAME, "div")
    ]

    parsed_listings = [parse_listing_html(li) for li in listings]
    r = pd.DataFrame(
        parsed_listings, columns=["link", "rent", "size", "property_type", "location"]
    )
    final.append(r)

    html = BeautifulSoup(
        driver.find_element(By.CLASS_NAME, "pager").get_attribute("outerHTML"),
        "html.parser",
    )
    urls = [
        e["href"] for e in html.find_all("a") if base_url + e["href"] not in visited
    ]
    driver.quit()

    for link in urls:
        try:
            get_listings(base_url + link, visited, final)
        except Exception as e:
            logging.warning(f"Cannot visit {link}: {e}")
    return r


def get_listing_attr(url):
    try:
        page = requests.get(url)
        page.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None, None, None, None

    soup = BeautifulSoup(page.content, "html.parser")
    html = soup.find("div", class_="top-info-mobile")
    title = html.findChild("h1").text
    street = html.findChild("strong").text
    description = soup.find("div", class_="desc").text
    seo = soup.find("div", class_="seo").text
    return title, street, description, seo


def listing_spider(root_url, base_url="https://www.housingtarget.com"):
    visited = set()
    final = []
    get_listings(root_url, visited, final, base_url)
    result = pd.concat(final)
    result.to_pickle(f"outputs/{root_url.split('/')[-1]}.pkl")
    logging.info(f"Saved results for {root_url}")
    return result


def fetch_attributes_in_parallel(df):
    url_lst = df["link"].map(lambda val : "https://www.housingtarget.com" + val)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        attrs = pool.map(get_listing_attr, url_lst)
    df[["title", "street", "description", "seo"]] = pd.DataFrame(attrs, index=df.index)
    return df


def run_spiders_in_parallel(root_urls):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(listing_spider, root_urls)
    all_results = pd.concat(results)
    logging.info("Finished scraping all listings.")
    return all_results


if __name__ == "__main__":
    ROOT_LIST = [
        "https://www.housingtarget.com/netherlands/housing-rentals/amsterdam",
        "https://www.housingtarget.com/netherlands/housing-rentals/utrecht",
        "https://www.housingtarget.com/netherlands/housing-rentals/eindhoven",
    ]
    all_listings = run_spiders_in_parallel(ROOT_LIST)
    all_listings = fetch_attributes_in_parallel(all_listings)
    current_time = str(datetime.datetime.now())
    output_path = f"outputs/all_listings_.pkl"
    all_listings.to_pickle(output_path)
    logging.info(f"Saved final dataset to {output_path}")
