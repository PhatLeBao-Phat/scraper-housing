from housing_scraper import website
import cProfile

def main():
    w = website.HousingTargetWebsite("https://www.housingtarget.com/netherlands/housing-rentals/amsterdam")
    visited_urls = set()
    return_listings = []
    lst = w.scrape_listings(visited_urls, return_listings, max_pages=4)

    return lst 

if __name__=="__main__":
    profiler = cProfile.Profile()

    # Run the function with profiling
    profiler.enable()
    main()
    profiler.disable()

    profiling_output_path = 'profiling_output.prof'  # Save as .prof file
    profiler.dump_stats(profiling_output_path)