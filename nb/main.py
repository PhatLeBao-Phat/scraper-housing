from housing_target_scraper import website
import cProfile
import pickle

URL = "https://www.housingtarget.com/netherlands/housing-rentals/eindhoven"

def main(url=URL):
    w = website.HousingTargetWebsite(url)
    visited_urls = set()
    return_listings = []
    lst = w.scrape_listings(visited_urls, return_listings, max_pages=20)

    return lst 

if __name__=="__main__":
    profiler = cProfile.Profile()

    # Run the function with profiling
    profiler.enable()
    lst = main()
    with open(f'outputs/{"_".join(URL.split("/")[-3:])}.pkl', 'wb') as f:
        pickle.dump(list, f)
    profiler.disable()

    profiling_output_path = 'profiling_output.prof'  # Save as .prof file
    profiler.dump_stats(profiling_output_path)