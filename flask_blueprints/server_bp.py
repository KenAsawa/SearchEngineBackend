import json
from urllib.parse import urlparse

from flask import Blueprint, jsonify, request

from search_engine import search, noise_words, index

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
        urls, titles, descriptions = search(query, case, noise)
        return jsonify({"urls": urls, "titles": titles, "descriptions": descriptions})

    return jsonify({"urls": [], "titles": [], "descriptions": []})


@server_ws.route("/echo-example")
def echo_example(socket):
    # Example usage of web socket to receive and send messages
    while not socket.closed:
        message = socket.receive()
        if message is None:
            continue
        message = json.loads(message)
        print("Received", message)
        # redis_set("message", message)  # Saving message to database
        response = json.dumps(message, default=str)
        # retrieve_message = redis_get("message")  # Getting message from database, do something with this if you want
        socket.send(response)
        print("Sent", message)
