from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Tuple
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import re
import multiprocessing
import requests

# Parse the listings
def _search_str_property(listing):
    size_match = re.search(r'(\d+\s*m2)', listing)
    size = size_match.group(1) if size_match else None

    # 2. Find the property type (e.g., apartment, house, room)
    type_match = re.search(r'\b(apartment|house|room)\b', listing, re.IGNORECASE)
    property_type = type_match.group(1) if type_match else None

    # 3. Find the location (everything after "in")
    location_match = re.search(r'(?<=\bin\s)(.*)', listing)
    location = location_match.group(1).strip() if location_match else None

    return (size, property_type, location)


def parse_listing_html(li_element : str) -> Tuple[str, int]:
    bs4_html = BeautifulSoup(li_element.get_attribute("outerHTML"), 'html.parser')
    link = bs4_html.find("a")["href"]
    rent = bs4_html.find("label").parent.find("span").text
    size, property_type, location = _search_str_property(bs4_html.find("a").text)

    return link, rent, size, property_type, location


def get_listings(url, visited, final, base_url='https://www.housingtarget.com'):
    """Get listings on a URL"""
    if url in visited:
        return
    print(f"Visiting {url}")
    visited.add(url)
    chrome_option = Options()
    chrome_option.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_option)
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

    # Recursive 
    html = BeautifulSoup(driver.find_element(By.CLASS_NAME, "pager").get_attribute("outerHTML"), "html.parser")
    urls = [e["href"] for e in html.find_all("a") if  base_url + e["href"] not in visited]
    driver.quit()

    for link in urls:
        try:
            get_listings('https://www.housingtarget.com' + link, visited, final)
        except Exception as e:
            # Handle exception if necessary
            print(f"Cannot visit {link}")
    return r


def get_listing_attr(url):
    try:
        page = requests.get(url, timeout=10)
        page.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None, None, None

    soup = BeautifulSoup(page.content, "html.parser")

    html = soup.find("div", class_="top-info-mobile") 
    
    title = html.findChild("h1").text
    street = html.findChild("strong").text
    description = soup.find_all("div", {"class" : "desc"})[0].text
    seo = soup.find_all("div", {"class" : "seo"})[0].text

    return title, street, description, seo


def listing_spider(root_url, base_url='https://www.housingtarget.com'):
    visited = set()
    final = []
    
    get_listings(root_url, visited, final, base_url)
    
    result = pd.concat(final)
    result.to_pickle(f"outputs/{root_url.split('/')[-1]}.pkl")
    return result


def run_spiders_in_parallel(root_urls):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(listing_spider, root_urls)
    
    # Combine the results
    all_results = pd.concat(results)
    return all_results


if __name__ == "__main__":
    ROOT_LIST = [
        "https://www.housingtarget.com/netherlands/housing-rentals/amsterdam",
        "https://www.housingtarget.com/netherlands/housing-rentals/utrecht",
        "https://www.housingtarget.com/netherlands/housing-rentals/eindhoven",
    ]
    
    # Run spiders in parallel
    all_listings = run_spiders_in_parallel(ROOT_LIST)
    all_listings.to_pickle("outputs/all_listings.pkl")
