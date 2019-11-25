import re

noise_words_file = open("Noisewords.txt", "r", encoding='utf8')
noise_words = set(line.strip() for line in noise_words_file.readlines())


def re_strip(string):
    """
    Removes all non-alphanumeric characters from the ends of the given string.
    :param string: a string to clean
    :return: A cleaned version of the string
    """
    pattern = "[^A-Za-z]"
    result = re.sub(f"^{pattern}+", "", string)
    result = re.sub(f"{pattern}+$", "", result)
    return result


def circular_shift(src_text, url, original, lowercase, title):  # Takes in a String, String, List, String
    # Return empty array if input line is empty
    if len(src_text) == 0:
        return {}, {}

    words = src_text.split(" ")
    # Clean words
    for index in range(len(words))[::-1]:
        words[index] = re_strip(words[index])
        if len(words[index]) == 0:
            words.pop(index)
    original_indexes = set()
    lowercase_indexes = set()
    shift_to_url = {}
    url_to_title = {}
    for i in range(len(words)):
        if words[0] not in noise_words:
            line = " ".join(words)
            original_indexes.add(line)
            lowercase_indexes.add(line.lower())

            if line not in shift_to_url:
                shift_to_url[line] = set()
            shift_to_url[line].add(url)

            if line.lower() not in shift_to_url:
                shift_to_url[line.lower()] = set()
            shift_to_url[line.lower()].add(url)

            url_to_title[url] = title
        # Shifts first word to the end
        words.append(words.pop(0))
    # Alphabetize the tuple list.
    original_indexes = sorted(list(original_indexes))
    lowercase_indexes = sorted(list(lowercase_indexes))
    # Merge new tuple list with main list
    original += original_indexes
    lowercase += lowercase_indexes
    return shift_to_url, url_to_title
