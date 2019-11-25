import os
import pickle

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

from circular_shifts import circular_shift
from scraper import scrape_url
from search_engine import original_shifts_list, lowercase_shifts_list, shift_to_url, url_to_title, noise_words, \
    set_globals, search

cred = credentials.Certificate("./searchEngine.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'searchengine-260015.appspot.com'
})

bucket = storage.bucket()


def index(url):
    print("Starting to scrape " + url)
    # Get website text
    try:
        scraped_text, title = scrape_url(url)
    except Exception as e:
        print(e)
        return
    # Circular shift it, get resulting associations
    shift_url_map, url_title_map = circular_shift(scraped_text, url, original_shifts_list, lowercase_shifts_list, title)
    # Now need to resort the main list
    original_shifts_list.sort()
    lowercase_shifts_list.sort()
    # Merge new shift/url map with existing map
    for shift in shift_url_map:
        if shift in shift_to_url:
            shift_to_url[shift] = shift_to_url[shift].union(shift_url_map[shift])
        else:
            shift_to_url[shift] = shift_url_map[shift]
    # Merge new url/title map with existing map
    url_to_title.update(url_title_map)
    print("Index creation for " + url + " complete")


def test_scraper():
    with open("./links_to_scrape.txt") as f:
        lines = f.readlines()
        for line in lines:
            if line[0] != "#":
                index(line.strip())


def create_file_and_upload(filename, file_obj):
    print("Starting upload for " + filename)
    os.system("rm " + filename)
    outfile = open(filename, 'wb')
    pickle.dump(file_obj, outfile)
    outfile.close()
    blob = bucket.blob(filename)
    blob.upload_from_filename("./" + filename)
    print("Upload complete for " + filename)


def upload_to_bucket():
    create_file_and_upload("original_shifts", original_shifts_list)
    create_file_and_upload("lowercase_shifts", lowercase_shifts_list)
    create_file_and_upload("shift_to_url", shift_to_url)
    create_file_and_upload("url_to_title", url_to_title)
    create_file_and_upload("noise_words", noise_words)


def download_file_and_create_object(filename):
    os.system("rm " + filename + "_download")
    file = bucket.blob(filename)
    file.download_to_filename(filename + "_download")
    infile = open(filename + "_download", 'rb')
    obj = pickle.load(infile)
    infile.close()
    return obj


def read_from_bucket():
    og_shift = download_file_and_create_object("original_shifts")
    lc_shift = download_file_and_create_object("lowercase_shifts")
    shift_url = download_file_and_create_object("shift_to_url")
    url_title = download_file_and_create_object("url_to_title")
    noise_w = download_file_and_create_object("noise_words")
    set_globals(original_sl=og_shift, lowercase_sl=lc_shift, shift_url=shift_url, url_title=url_title, noises=noise_w)


def push_to_db():
    db = firestore.client()
    batch = db.batch()

    og_shifts = db.collection('Refs').document('OriginalShifts')
    batch.set(og_shifts, {'original_shifts': original_shifts_list}, merge=True)

    batch.commit()

    batch = db.batch()

    lc_shifts = db.collection('Refs').document('LowerCaseShifts')
    batch.set(lc_shifts, {'lowercase_shifts': lowercase_shifts_list}, merge=True)

    batch.commit()

    for key in shift_to_url:
        shift_to_url[key] = list(shift_to_url[key])

    batch = db.batch()

    shift_urls = db.collection('Refs').document('ShiftToUrls')
    batch.set(shift_urls, {'shift_to_url': shift_to_url}, merge=True)

    batch.commit()

    batch = db.batch()

    url_titles = db.collection('Refs').document('UrlToTitle')
    batch.set(url_titles, {'url_to_title': url_to_title}, merge=True)

    batch.commit()

    noise_words_list = list(noise_words)

    batch = db.batch()

    noises = db.collection('Refs').document('NoiseWords')
    batch.set(noises, {'noise_words': noise_words_list}, merge=True)

    batch.commit()


def main():
    # test_scraper()
    # upload_to_bucket()
    # push_to_db()
    read_from_bucket()
    while True:
        query = input('Search Query: ')
        case = (input('Case sensitive? (type "yes", default no): ').lower() + ' ')[0] == 'y'
        urls, titles, descriptions = search(query, case)
        print(urls)
        print(titles)
        print(descriptions)


if __name__ == '__main__':
    main()
