from circular_shifts import circular_shift
from scraper import scrape_url


def main():
    url = "https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python"
    scraped_text = scrape_url(url)
    shifts_map = {}
    shift = circular_shift(scraped_text, url, shifts_map)
    shifts_map.update(shift)
    print(shifts_map)


main()
