from search_engine import noise_words, search, init_index


def main():
    init_index()

    while True:
        query = input('Search Query: ')
        case = (input('Case sensitive? (type "yes", default no): ').lower() + ' ')[0] == 'y'
        urls, titles, descriptions = search(query, case, noise_words)
        print(urls)
        print(titles)
        print(descriptions)


if __name__ == '__main__':
    main()
