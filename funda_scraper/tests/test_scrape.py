import pytest
from funda_scraper.scrape import FundaScraper

# Setup fixture
@pytest.fixture(scope="function")
def setup_teardown():
    # Setup
    print("Setup")
    
    scraper = FundaScraper(
        area="Eindhoven", 
        want_to="rent", 
        find_past=False, 
        page_start=1, 
        min_price=500, 
        max_price=2000
    )

    yield scraper 

    # Teardown (if necessary)
    print("Teardown")

def test_fix_link(setup_teardown):
    url = "https://www.funda.nl/detail/huur/eindhoven/appartement-cassandraplein-5-18/89233315/"
    expected_result = "https://www.funda.nl/detail/huur/eindhoven/appartement-cassandraplein-5-18/89233315/?old_ldp=true"
    
    # Assert with a message for better readability on failure
    assert setup_teardown.fix_link(url) == expected_result, f"Expected {expected_result}, but got {setup_teardown.fix_link(url)}"
