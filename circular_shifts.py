noise_words_file = open("Noisewords.txt", "r", encoding='utf8')
noise_words = set(line.strip() for line in noise_words_file.readlines())


def circular_shift(src_text, url, main_list, title):  # Takes in a String, String, List, String
    # Return empty array if input line is empty
    if len(src_text) == 0:
        return main_list
    words = src_text.split(" ")
    indexes = set()
    shift_to_url = {}
    url_to_title = {}
    for i in range(len(words)):
        if words[0] not in noise_words:
            line = " ".join(words)
            indexes.add(line)
            if line not in shift_to_url:
                shift_to_url[line] = set().add(url)
            else:
                shift_to_url[line] = shift_to_url[line].get(line, []).add(url)
            url_to_title[url] = title
        # Shifts first word to the end
        words.append(words.pop(0))
    # Alphabetize the tuple list.
    indexes = sorted(list(indexes), key=lambda s: s[0].lower())
    # Merge new tuple list with main list
    main_list += indexes
    return main_list
