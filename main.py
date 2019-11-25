from circular_shifts import circular_shift
from scraper import scrape_url
from search_engine import search, shifts_list, shift_to_url, url_to_title


def index(url):
    print("Starting to scrape " + url)
    # Get website text
    scraped_text, title = scrape_url(url)
    # Circular shift it, get resulting associations
    shift_url_map, url_title_map = circular_shift(scraped_text, url, shifts_list, title)
    # Now need to resort the main list
    shifts_list.sort(key=lambda s: s.lower())
    # Merge new shift/url map with existing map
    for shift in shift_url_map:
        if shift in shift_to_url:
            shift_to_url[shift] = shift_to_url[shift].union(shift_url_map[shift])
        else:
            shift_to_url[shift] = shift_url_map[shift]
    # Merge new url/title map with existing map
    url_to_title.update(url_title_map)
    print("Index creation for " + url + " complete")


def test_scraper():
    with open("./links_to_scrape.txt") as f:
        lines = f.readlines()
        for line in lines:
            index(line.strip())


def find():
    for start in shifts_list:
        for end in shifts_list[::-1]:
            for word in start.split(" "):
                if word in end:
                    print(word)
                    # return word


def main():
    test_scraper()
    # index("https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python")
    # find()
    while True:
        query = input('Search Query: ')
        case = (input('Case sensitive? (type "yes", default no): ').lower() + ' ')[0] == 'y'
        urls, titles, descriptions = search(query, case)
        print(urls)
        print(titles)
        print(descriptions)


if __name__ == '__main__':
    main()
