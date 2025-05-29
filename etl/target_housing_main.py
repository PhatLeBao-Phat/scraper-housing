from pathlib import Path
from datetime import datetime 
import json
import os

from housing_target_scraper.scraper import TargetHousingScraper

# Utils 
class TargetHousingIngestionPipeline:
    """
    Pipeline for ingesting housing data using a configuration file.
    :param config_path: Path to the configuration JSON file.
    """
    def __init__(self, config_path: Path):
        self.config_path = config_path

    def get_config(self):
        with open(self.config_path, "r") as file:
            config = json.load(file)
        return config
    
    def execute(self):
        config = self.get_config()

        scraper = TargetHousingScraper()
        scraper.set_search_url(
            # zipcodes=[1048, 1315],
            location_queries="Amsterdam",
            housing_type=["Apartment", "Home"], 
            min_price=10,
            max_price=1100,
            min_size=1,
            max_size=100,
            extra_criteria=["more 1 year", "unlimited"]
        )
        results = [d for d in scraper.scrape()]
        results_df = TargetHousingScraper.to_dataframe(results)

        current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        snapshot_date = datetime.now().strftime("%d-%m-%Y")
        target_path = Path(config["target_path"]) / f"snapshot_date={snapshot_date}"
        if not os.path.exists(target_path):
            os.mkdir(target_path)
        results_df.to_json(target_path / f"{current_time}.json", orient="records", lines=True)



if __name__ == "__main__":
    config_path = r"C:\Users\PC\Documents\Personal Projects\9. scraper-housing\scraper-housing\configs\target_housing_config.json"
    pipeline = TargetHousingIngestionPipeline(
        config_path=config_path
    )
    pipeline.execute()