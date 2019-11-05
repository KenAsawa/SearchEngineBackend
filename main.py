from timeit import default_timer as timer

from circular_shifts import circular_shift
from scraper import scrape_url


def main():
    url = "https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python"
    start = timer()
    scraped_text = scrape_url(url)
    end = timer()
    print("Total time taken to scrape text:", end - start, "seconds")
    shifts_map = {}
    start = timer()
    shift = circular_shift(scraped_text, url, shifts_map)
    shifts_map.update(shift)
    end = timer()
    print("Total time taken to shift and merge:", end - start, "seconds")
    # print(shifts_map)


main()
