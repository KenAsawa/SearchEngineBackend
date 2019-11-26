#!/usr/bin/env python3
"""
Usage:

    ./server.py -h
    ./server.py -l localhost -p 8000
"""

import argparse
import cgi
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from search_engine import search, index


class SearchEngineServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        content_type, p_dict = cgi.parse_header(self.headers.get('content-type'))

        # refuse to receive non-json content
        if content_type != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        payload_string = self.rfile.read(length).decode('utf-8')
        payload = json.loads(payload_string) if payload_string else {}

        # Build return response
        response = {}

        # Search query event
        if 'query' in payload and 'case_sensitive' in payload:
            urls, titles, descriptions = search(payload['query'], payload['case_sensitive'])
            response['urls'], response['titles'], response['descriptions'] = urls, titles, descriptions

        # Index a new site
        elif 'index' in payload:
            try:
                index(payload['index'])
                response['complete'] = True
            except:
                response['complete'] = False

        # Search input
        elif 'autofill' in payload:
            response['complete'] = False

        # Anything else
        else:
            response['complete'] = False

        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))


def run(server_class=ThreadingHTTPServer, handler_class=SearchEngineServer, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print("Starting httpd server on {}:{}".format(addr, port))
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
