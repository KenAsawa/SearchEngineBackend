import os
import platform
import signal
import subprocess
from subprocess import Popen, PIPE

from flask import Flask, render_template
from flask_blueprints.server_bp import server_bp
from flask_blueprints.server_bp import server_ws
from flask_cors import CORS
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

operating_system = str(platform.system()).lower()

app = Flask(__name__, static_folder="static", template_folder="templates")

CORS(app)

# Disables caching for each flair app that uses PyWebView
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1

# Registers webview API's under /webview/<api-name> to keep code separate and clean
app.register_blueprint(server_bp, url_prefix='/server_bp')

ws = Sockets(app)

ws.register_blueprint(server_ws, url_prefix='/server_ws')


@app.after_request
def add_header(response):
    """
        Disables caching for each flair app that uses PyWebView
    """
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route("/")
def home():
    """
        Templates should be stored inside templates folder
    """
    return render_template("index.html")


def kill_port(port):
    process = Popen(["lsof", "-i", ":{0}".format(port)], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    for process in str(stdout.decode("utf-8")).split("\n")[1:]:
        data = [x for x in process.split(" ") if x != '']
        if len(data) <= 1:
            continue

        os.kill(int(data[1]), signal.SIGKILL)


def run_app(url, port, start_redis):
    if "darwin" in operating_system:
        if start_redis:
            subprocess.run("brew services stop redis && brew services start redis", shell=True)
        kill_port(port)
    server = pywsgi.WSGIServer((url, port), app, handler_class=WebSocketHandler)
    server.serve_forever()
    # app.run(host=url, port=port, threaded=True)


if __name__ == '__main__':
    """
        App can be launched from this file itself
        without needing to package or launch Window.
        Can be useful for chrome tools debugging. Make sure port number
        is the same as in flair.py
    """
    run_app('localhost', port=8000, start_redis=False)
