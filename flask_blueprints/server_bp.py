import json

from flask import Blueprint, jsonify, request

from search_engine import search

server_bp = Blueprint('server_bp', __name__)
server_ws = Blueprint('example_ws', __name__)


@server_bp.route("/search", methods=["POST"])
def start_dialog():
    if request.method == "POST":
        body = request.json
        print(body)
        urls, titles, descriptions = search(body['query'], body['case_sensitive'])
        return jsonify({"urls": urls, "titles": titles, "descriptions": descriptions})
    jsonify({"urls": [], "titles": [], "descriptions": []})


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
