from urllib.parse import urlparse

from flask import Blueprint, jsonify, request

from search_engine import search, noise_words, index, auto_fill_find
import math

server_bp = Blueprint('server_bp', __name__)
server_ws = Blueprint('server_ws', __name__)


@server_bp.route("/noise-words", methods=["GET"])
def get_noise():
    return jsonify({"noise_words": list(noise_words)})


@server_bp.route("/index", methods=["POST"])
def live_index():
    if request.method == "POST":
        body = request.json
        url = body['url'] if 'url' in body else None
        if url is not None:
            parse = urlparse(url)
            if parse.scheme != '' and parse.netloc != '':
                result = index(url)
                if result is None:
                    return jsonify(
                        {"status": 2, "message": "'{}' was unable to be scraped. Please try again.".format(url)})
                elif result is 1:
                    return jsonify(
                        {"status": 2, "message": "'{}' was already indexed.".format(url)})
                else:
                    return jsonify({"status": 1, "message": "'{}' was successfully indexed.".format(url)})
            else:
                return jsonify({"status": 2, "message": "Error: Malformed URL."})
        else:
            return jsonify({"status": 2, "message": "Error: No URL provided."})


@server_bp.route("/search", methods=["POST"])
def search_index():
    if request.method == "POST":
        body = request.json
        query = body['query'] if 'query' in body else ''
        case = body['case_sensitive'] if 'case_sensitive' in body else False
        noise = body['noise_words'] if 'noise_words' in body else []
        noise = [word['word'] for word in noise]
        ordering = body['ordering'] if 'ordering' in body else False
        results_per_page = body['results_per_page'] if 'results_per_page' in body else 1
        urls, titles, descriptions = search(query, case, noise, ordering)
        if results_per_page == 1:
            num_of_pages = len(urls)
        else:
            num_of_pages = math.ceil(len(urls) / results_per_page)
        return jsonify({"urls": urls, "titles": titles, "descriptions": descriptions, "num_of_pages": num_of_pages})

    return jsonify({"urls": [], "titles": [], "descriptions": [], "num_of_pages": 0})


@server_bp.route("/auto-fill", methods=["POST"])
def auto_fill():
    if request.method == "POST":
        body = request.json
        message = body['query']
        auto_fill_choices = auto_fill_find(message)
        return jsonify({"auto_fill": auto_fill_choices})

    return jsonify({"auto_fill": []})
