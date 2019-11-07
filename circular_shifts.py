noise_words_file = open("Noisewords.txt", "r", encoding='utf8')
noise_words = set(line.strip() for line in noise_words_file.readlines())


def circular_shift(src_text, url, main_list):  # Takes in a String, String, List
    # Return empty array if input line is empty
    if len(src_text) == 0:
        return
    words = src_text.split(" ")
    indexes = []
    for i in range(len(words)):
        if words[0] not in noise_words:
            line = " ".join(words)
            # Appends tuple to list of tuple
            new_index = [line, url]
            indexes.append(new_index)
        # Shifts first word to the end
        words.append(words.pop(0))
    # Alphabetize the tuple list.
    indexes = sorted(indexes, key=lambda s: s[0].lower())
    # Merge new tuple list with main list
    main_list += indexes
    return main_list
