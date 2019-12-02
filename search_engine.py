import copy
import json
import os

from readerwriterlock import rwlock

from circular_shifts import circular_shift
from scraper import scrape_url

# Reader/Writer Mutex Lock
database_lock = rwlock.RWLockFair()

# Data
original_shifts_list = []
lowercase_shifts_list = []
shift_to_url = {}
url_to_title = {}
noise_words = [line.strip() for line in open("Noisewords.txt", "r", encoding='utf8').readlines()]
noise_words.sort()
noise_words = set(noise_words)

# Server status
started = False


def init_index():
    global started

    if os.path.exists("original_shifts.json") and \
            os.path.exists("lowercase_shifts.json") and \
            os.path.exists("shift_to_url.json") and \
            os.path.exists("url_to_title.json") and \
            os.path.exists("noise_words.json"):
        read_from_file()

    with open("./links_to_scrape.txt") as f:
        for line in f.readlines():
            if line[0] != "#":
                index(line.strip())

    started = True
    write_to_file()


def read_from_file():
    global original_shifts_list
    global lowercase_shifts_list
    global shift_to_url
    global url_to_title
    global noise_words

    with database_lock.gen_wlock():
        print("Reading from disk cache. This may take a while...")
        original_shifts_list = read_from_json("original_shifts")
        lowercase_shifts_list = read_from_json("lowercase_shifts")
        shift_to_url = read_from_json("shift_to_url")
        shift_to_url = {key: set(shift_to_url[key]) for key in shift_to_url}
        url_to_title = read_from_json("url_to_title")
        noise_words = read_from_json("noise_words")
        noise_words = set(noise_words)
        print("Loading from disk successful.")


def read_from_json(filename):
    with open(filename + ".json") as json_file:
        data = json.load(json_file)
        return data


def write_to_file():
    with database_lock.gen_rlock():
        print("Writing to disk cache. This may take a while...")
        write_to_json("original_shifts", original_shifts_list)
        write_to_json("lowercase_shifts", lowercase_shifts_list)
        write_to_json("shift_to_url", {key: list(shift_to_url[key]) for key in shift_to_url})
        write_to_json("url_to_title", url_to_title)
        write_to_json("noise_words", list(noise_words))
        print("Write to disk finished.")


def write_to_json(filename, file_obj):
    with open(filename + ".json", 'w') as outfile:
        json.dump(file_obj, outfile)


def auto_fill_find(string):
    """
    Finds up to 5 possible strings that start with the string given so far.
    :param string: the query of the user so far
    :return: a list of suggested auto-fill results
    """

    # Assume lowercase for the string
    string = string.lower().strip()

    # Base case
    if len(string) == 0:
        return []

    # Find an index that starts with the given string
    with database_lock.gen_rlock():
        left, mid, right = 0, None, len(lowercase_shifts_list)
        while left <= right:
            mid = int((left + right) / 2)
            # Check if match found at mid
            if lowercase_shifts_list[mid].startswith(string):
                break
            # If we're too far in the list
            elif string < lowercase_shifts_list[mid]:
                right = mid - 1
            # If we're not far enough in the list
            else:
                left = mid + 1
        else:
            # Only make mid None if while loop was intentionally broken
            mid = None

        # No partial match found
        if mid is None:
            return []

        # Go backwards until the first partial match
        while lowercase_shifts_list[mid].startswith(string):
            mid -= 1

        # Increment to first partial match
        mid += 1
        # Generate auto-fill results
        auto_fill_results = set()
        while len(auto_fill_results) < 5:  # Max of 5 results
            current_shift = lowercase_shifts_list[mid]
            if current_shift.startswith(string):
                # Generate only a few words or characters out
                num_spaces, position = 0, len(string)
                while num_spaces < 3 and position < len(current_shift) and position < len(string) + 20:
                    if current_shift[position] == " ":
                        num_spaces += 1
                    position += 1
                auto_fill_results.add(current_shift[:position].strip())
                mid += 1
            else:
                break

        return list(auto_fill_results)


def index(url):
    global original_shifts_list
    global lowercase_shifts_list
    global shift_to_url
    global url_to_title

    if url in url_to_title:
        print("'{}' has already been indexed.".format(url))
        return 1

    with database_lock.gen_rlock():
        osl = copy.deepcopy(original_shifts_list)
        lsl = copy.deepcopy(lowercase_shifts_list)
        stu = copy.deepcopy(shift_to_url)
        utt = copy.deepcopy(url_to_title)

    print("Indexing " + url)
    # Get website text
    try:
        scraped_text, title = scrape_url(url)
    except Exception as e:
        print(e)
        return None
    # Circular shift it, get resulting associations
    shift_url_map, url_title_map = \
        circular_shift(scraped_text, url, osl, lsl, title)
    # Now need to resort the main list
    osl.sort()
    lsl.sort()
    # Merge new shift/url map with existing map
    for shift in shift_url_map:
        if shift in stu:
            stu[shift] = stu[shift].union(shift_url_map[shift])
        else:
            stu[shift] = shift_url_map[shift]
    # Merge new url/title map with existing map
    utt.update(url_title_map)

    with database_lock.gen_wlock():
        original_shifts_list = osl
        lowercase_shifts_list = lsl
        shift_to_url = stu
        url_to_title = utt

    if started:
        with database_lock.gen_rlock():
            write_to_file()

    print("Index creation for " + url + " complete")
    return True


def binary_search(arr, word, case_sensitive=False):
    """
    Returns the index in an array of KWIC indices
    """

    # Force lowercase if case insensitive
    if not case_sensitive:
        word = word.lower()

    return recursive_binary_search(arr, word, 0, len(arr) - 1, case_sensitive)


def recursive_binary_search(array, word, left, right, case_sensitive):
    """
    Recursively performs binary search on an array of indices. Comparisons
    are done based on alphabetical order of current "mid" value and the word
    to search for.
    :param array: list of strings to search in
    :param word: string to search for
    :param left: left possible index of word in array
    :param right: right possible index of word in array
    :param case_sensitive: True if case sensitivity should be enforced
    :return: the index that the word is contained at, -1 if not found.
    """

    # Stop if no indices left to search
    if right < left:
        return -1

    # Compute middle index
    mid = int((left + right) / 2)
    # Get middle word
    mw = array[mid].split(' ')[0]

    # Return desired index accordingly
    if word == mw:
        return mid
    if word < mw:
        return recursive_binary_search(array, word, left, mid - 1, case_sensitive)
    if word > mw:
        return recursive_binary_search(array, word, mid + 1, right, case_sensitive)


def parse_keyword_combinations(search_query):
    """
    Parses the given query and determines what groupings of tokens must appear
    in returned search results. Output consists of a list, where each member is
    a list of tokens. The contents of one sub-list indicates queries where all
    contained tokens must match for any given result.
    :param search_query: a string of space separated keywords
    :return: a tuple containing a list of clauses, where each clause is a list of
    keywords AND'd together and the clauses themselves are OR'd together, and a set
    of strings containing the keywords that have been NOT'd.
    """

    # Tokenize search query
    tokenized = search_query.split(' ')
    # ORs are implied; filter them out
    tokenized = [term for term in tokenized if term != "OR"]
    # Remove leading/trailing ANDs
    if len(tokenized) > 0 and tokenized[0] == 'AND':
        tokenized.pop(0)
    if len(tokenized) > 0 and tokenized[-1] == 'AND':
        tokenized.pop()
    # Remove trailing NOT
    if len(tokenized) > 0 and tokenized[-1] == 'NOT':
        tokenized.pop()

    # Find locations of keyword "NOT"
    not_locations = [i for i in range(len(tokenized)) if tokenized[i] == 'NOT']
    # Get list of terms that are to be negative
    negations = set([tokenized[i + 1] for i in not_locations])
    # NOT terms and associate keywords can now be removed
    for i in not_locations[::-1]:
        tokenized.pop(i + 1)  # keyword
        tokenized.pop(i)  # NOT

    # Find locations of actual keywords
    keyword_locations = [i for i in range(len(tokenized)) if tokenized[i] != 'AND']
    # Each clause if a series of terms ANDed together
    clauses, clause_num = [], 0
    for pos in range(len(keyword_locations)):
        # See if new sublist needs to be made
        if clause_num == len(clauses):
            clauses.append([])
        # Add current keyword to current AND chain
        clauses[clause_num].append(tokenized[keyword_locations[pos]])
        # If next keyword is next in tokenized
        if pos + 1 < len(keyword_locations) and keyword_locations[pos + 1] == keyword_locations[pos] + 1:
            # New clause will begin
            clause_num += 1

    # Convert to simple space-separate strings
    # for i in range(len(clauses)):
    #     clauses[i] = ' '.join(clauses[i])

    # Return list of OR'd AND clauses and list of blacklisted words
    return clauses, negations


def contains_words(index_string, words, case_sensitive):
    """
    Determines if the given index_string contains all tokens within words.
    :param index_string: The string within which to search for tokens
    :param words: The list of tokens to find in the index_string
    :param case_sensitive: True if differences in case matter, False otherwise
    :return: True if all words are found in the index_string, False otherwise
    """

    # Base case
    if len(words) == 0:
        return True

    # Remove duplicates, hash contents
    words = set(words)
    # Case sensitivity
    if case_sensitive:
        index_string = index_string.lower()

    # Iterate through index_string
    for token in index_string.split(' '):
        # Case sensitivity
        if case_sensitive:
            token = token.lower()
        # Check this is one of the words
        if token in words:
            # Stop checking for that word
            words.remove(token)
            # All words found? Return True
            if len(words) == 0:
                return True

    return False


def filter_clauses(clauses, stop_words):
    """
    Filters all stop words from a predetermined list of stop words.
    Additionally filters any clauses that become empty as a result.
    :param clauses: A list of lists representing clauses of OR'd terms.
    :param stop_words: A list or set of strings that are words to be filtered out.
    :return: A list containing clauses post-filtering.
    """

    # Iterate backwards through the clause list
    for clause_position in range(len(clauses))[::-1]:
        current_clause = clauses[clause_position]
        # Iterate backwards through the current clause
        for token_position in range(len(current_clause))[::-1]:
            # Remove word if it is a noise word
            if current_clause[token_position].lower() in stop_words:
                current_clause.pop(token_position)

        # Remove the clause altogether if nothing left
        if len(current_clause) == 0:
            clauses.pop(clause_position)

    return clauses


def search(search_query, case_sensitive, noise):
    """
    Searches the index for results matching the search query.
    :param search_query: the string input from a user's search query
    :param case_sensitive: whether or not this query will be case sensitive
    :param noise: words that should be ignored altogether.
    :return: a list of URLs and parallel lists of corresponding titles and descriptions
    """

    with database_lock.gen_rlock():
        for i in range(len(noise)):
            noise[i] = noise[i].lower()

        # Parse into clauses to match and blacklist to avoid
        clause_list, blacklist = parse_keyword_combinations(search_query)

        # Make case irrelevant if needed
        if not case_sensitive:
            for c in clause_list:
                for pos in range(len(c)):
                    c[pos] = c[pos].lower()

        # Which index list to search in
        target_list = original_shifts_list if case_sensitive else lowercase_shifts_list

        # Filter all noise words and prune empty clauses from clause list.
        clause_list = filter_clauses(clause_list, noise)

        results = []
        # go through each clause
        for c in clause_list:
            # find matching index position based on first term in clause
            position = binary_search(target_list, c[0], case_sensitive=case_sensitive)
            # Ignore if no initial match found
            if position == -1:
                continue

            # Get all matches
            indices = []
            # Scan for matches going backwards
            temp = position
            while target_list[temp].split(' ')[0] == c[0]:
                indices.append(temp)
                temp -= 1
            # Scan for matches going forwards
            temp = position + 1
            while target_list[temp].split(' ')[0] == c[0]:
                indices.append(temp)
                temp += 1

            for position in indices:
                # Ignore if match contains words that were blacklisted
                if len(blacklist) > 0 and contains_words(target_list[position], blacklist,
                                                         case_sensitive=case_sensitive):
                    continue
                # Ignore if match doesn't have remaining words in clause
                if not contains_words(target_list[position], c[1:], case_sensitive=case_sensitive):
                    continue
                # Match must be good
                results.append(target_list[position])
        results = set(results)

        # All urls to return
        urls = set()
        for shift in results:
            urls = urls.union(shift_to_url[shift])
        urls = list(urls)

        # All titles
        titles = [url_to_title[url] for url in urls]

        # Generate descriptions
        not_described = urls.copy()
        descriptions = []
        for shift in results:
            for url in shift_to_url[shift]:
                if url in not_described:
                    if len(shift) < 170:
                        descriptions.append(shift)
                    else:
                        descriptions.append(shift[:170] + '...')
                    not_described.remove(url)

        # Return
        return urls, titles, descriptions
