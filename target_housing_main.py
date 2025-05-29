import pickle
from pathlib import Path
from datetime import datetime 

from housing_target_scraper.scraper import TargetHousingScraper


OUTPUT_DIR = Path(__file__).parent.joinpath("outputs")

# This will run the asynchronous main function and handle the event loop
if __name__ == "__main__":
    scraper = TargetHousingScraper()
    url = scraper.set_search_url(
        zipcodes=[1048, 1315],
        # location_queries="Amsterdam",
        # housing_type=["Apartment", "Home"], 
        # min_price=10,
        max_price=1100,
        # min_size=1,
        # max_size=100,
        extra_criteria=["more 1 year", "unlimited"]
    )
    results = [d for d in scraper.scrape()]
    results_df = TargetHousingScraper.to_dataframe(results)
    print(results_df.head(50))
    print(results[0])

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # with open(OUTPUT_DIR.joinpath(f"{current_time}.pkl"), "wb") as file:
        # pickle.dump(print_results, file)
    
    results_df.to_json(OUTPUT_DIR.joinpath(f"{current_time}.json"), orient="records", lines=True)


