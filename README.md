# scraper-housing
This project is a web scraper designed to collect housing listings from HousingTarget.com. It automates the process of gathering property details such as location, price, size, and description. Additionally, it estimates travel time to the ABN AMRO HQ using the NS API and optimizes performance through parallel processing. We listed here the intended features:
- Scrapes housing data from HousingTarget.com
- Filters listings based on city (Eindhoven, Amsterdam, Rotterdam)
- Calculates travel distance to ABN AMRO HQ using NS API
- Optimized with multiprocessing for faster execution
- Recommend and alert the potential housing
## 1. Project Layout
```bash
scraper-housing/
|-- logs            # Fork the processing
|-- src             # ns APIs fork 
|-- scraper.py      # Main scraper script 
|-- config.cfg      # Config file 
|-- outputs         # Temp storage for ETLs
```
## 2. Items 
function to pull places/stations/etc... based on the query and country 
-> return object of all kinds?
-> TODO: Write `get_places` function in ns api