from search_engine import index, write_to_file

with open("./links_to_scrape.txt") as f:
    for line in f.readlines():
        if line[0] != "#":
            index(line.strip())
    write_to_file()
