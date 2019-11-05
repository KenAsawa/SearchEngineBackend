
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

# Set case sensitivity setting
sensitivity = input('Type "1" to enable case sensitivity: ') == '1'

query = input('Search Query: ')
for token in query.split(' '):
    index = binarySearchIndex(indices, token, case_sensitive=sensitivity)
    if index == -1:
        print('{} not found.'.format(token))
    else:
        print('{} found at index {}.'.format(token, index))

