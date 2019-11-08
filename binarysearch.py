def binarySearchIndex(arr, word, case_sensitive=False):
    """
    Returns the index in an array of KWIC indices 
    """

    # Force lowercase if case insensitive
    if not case_sensitive:
        word = word.lower()

    return recursiveBinarySearch(arr, word, 0, len(arr) - 1, case_sensitive)


def recursiveBinarySearch(array, word, left, right, case_sensitive):
    # Stop if no indices left to search
    if right < left:
        return -1

    # Compute middle index
    mid = int((left + right) / 2)
    # Get middle word
    mw = array[mid][0].split(' ')[0]
    # Force lowercase if case insensitive
    if not case_sensitive:
        mw = mw.lower()

    # Return desired index accordingly
    if mw == word:
        return mid
    if word < mw:
        return recursiveBinarySearch(array, word, left, mid - 1, case_sensitive)
    if word > mw:
        return recursiveBinarySearch(array, word, mid + 1, right, case_sensitive)


def parseOperators(search_query):
    """
    Parses the given query and determines what groupings of tokens must appear
    in returned search results. Output consists of a list, where each member is
    a list of tokens. The contents of one sub-list indicates queries where all
    contained tokens must match for any given result.
    :param search_query:
    :return:
    """
    # Each clause if a series of terms ANDed together
    clauses = []

    # Tokenize search query
    tokenized = search_query.split(' ')
    # ORs are implied; filter them out
    tokenized = [term for term in tokenized if term != "OR"]
    # Remove leading/trailing ANDs
    if tokenized[0] == 'AND':
        tokenized.pop(0)
    if tokenized[-1] == 'AND':
        tokenized.pop()
    # Remove trailing NOT
    if tokenized[-1] == 'NOT':
        tokenized.pop()

    # Find locations of keyword "NOT"
    not_locations = [i for i in range(len(tokenized)) if tokenized[i] == 'NOT']
    # Get list of terms that are to be negative
    negations = [tokenized[i + 1] for i in not_locations]

    # Find locations of keyword "NOT"
    and_locations = [i for i in range(len(tokenized)) if tokenized[i] == 'AND']
    # Clause this is a part of
    clause_number = -1
    for i in range(len(and_locations)):
        current_location = and_locations[i]
        # ANDs chained together
        if i > 1 and current_location == and_locations[i - 1] + 2:
            clauses[clause_number].add(tokenized[current_location - 1])
            clauses[clause_number].add(tokenized[current_location + 1])
        # New AND chain
        else:
            clauses.append(set())
            clause_number += 1
            clauses[clause_number].add(tokenized[current_location - 1])
            clauses[clause_number].add(tokenized[current_location + 1])

    # Convert to simple space-separate strings
    for i in range(len(clauses)):
        clauses[i] = ' '.join(clauses[i])

    # Return list of OR'd AND clauses and list of blacklisted words
    return clauses, negations


indices = [
    ('bunny monday', ['url', 'url']),
    ('cat', ['url', 'url']),
    ('dog', ['url', 'url']),
    ('engine', ['url', 'url']),
    ('hard wall', ['url', 'url']),
    ('jump', ['url', 'url']),
    ('monday bunny', ['url', 'url']),
    ('tuesday', ['url', 'url']),
    ('wall hard', ['url', 'url']),
]
indices.sort(key=lambda s: s[0].lower())


def test_querying():
    # Set case sensitivity setting
    sensitivity = input('Type "1" to enable case sensitivity: ') == '1'
    query = input('Search Query: ')
    for token in query.split(' '):
        index = binarySearchIndex(indices, token, case_sensitive=sensitivity)
        if index == -1:
            print('{} not found.'.format(token))
        else:
            print('{} found at index {}.'.format(token, index))


def test_op_parsing():
    query = input('Search Query: ')
    c, n = parseOperators(query)

    print('AND combinations:')
    for comb in c:
        print(comb)

    print('\nNOT words:')
    for word in n:
        print(word)


if __name__ == '__main__':
    test_op_parsing()
