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
                try:
                    index(url)
                    return jsonify({"status": 1, "message": "'{}' was successfully indexed.".format(url)})
                except Exception as e:
                    return jsonify({"status": 2, "message": "An error occurred. Please try again."})
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
        urls, titles, descriptions = search(query, case, noise if type(noise) is list else [])
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
