# Function
def circular_shift(shifts_text, shifts_url, shifts_map):  # Takes in a String, String, & Dictionary
    url_list = [shifts_url]
    # Split source text by spaces.
    words = shifts_text.split()
    # Return empty array if input line is empty
    if len(shifts_text) == 0:
        return []
    lines = {}
    # Checks current dictionary for the shifts_text, if it exists, adds old urls to the new url.
    for i in sorted(shifts_map.items()):
        if i[0] == (shifts_text + " "):
            for oldUrl in i[1]:
                if oldUrl != shifts_url:
                    url_list.append(oldUrl)
    # Number of lines to be generated = number of words
    for num_words in range(len(words)):
        line = ""
        for word in words:
            line += word + " "
        # Appends tuple to list of tuple
        lines[line] = url_list
        # Shifts first word to the end
        words.append(words.pop(0))
    return lines


def print_sorted_dict_items(shifts_map):
    for i in sorted(shifts_map.items(), key=lambda x: x[0].lower()):
        print(i, end="\n")


def print_sorted_dict_keys(shifts_map):
    for i in sorted(shifts_map.keys(), key=str.lower):
        print(i, end="\n")