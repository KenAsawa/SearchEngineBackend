import nltk
from nltk import tokenize
# Run this line to download the package.
# nltk.download('punkt')

noise_words_file = open("Noisewords.txt", "r", encoding='utf8')
noise_words_list = noise_words_file.read().split()


def circular_shift(src_text, url, main_list):  # Takes in a String, String, List, String
    # Return empty array if input line is empty
    if len(src_text) == 0:
        return
    # Split source text by sentences.
    sentences = tokenize.sent_tokenize(src_text)  # Magic function that splits text into sentences.
    new_tuple_list = []
    for sentence in sentences:
        # Splits sentences by words.
        words = nltk.word_tokenize(sentence)
    # Number of lines to be generated = number of words
        for num_words in range(len(words)):
            # Denoise noise words.
            if words[0] not in noise_words_list:
                line = ""
                for word in words:
                    line += word + " "
                # Appends tuple to list of tuple
                new_tuple = (line[:-1], url)
                new_tuple_list.append(new_tuple)
            # Shifts first word to the end
            words.append(words.pop(0))
    # Alphabetize the tuple list.
    new_tuple_list = sorted(new_tuple_list, key=lambda s: s[0].lower())
    # Merge new tuple list with main list
    main_list += new_tuple_list
    #mergeSort(main_list)
    main_list = sorted(main_list, key=lambda s: s[0].lower())