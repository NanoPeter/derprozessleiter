from flask import Flask , jsonify
from xmlrpc.client import ServerProxy
import json

url = 'http://localhost:8000/process-manager'

app = Flask(__name__, static_folder='./static/', static_url_path='/static')

@app.route('/list', methods=['GET'])
def list():
    with ServerProxy(url) as proxy:
        processes = proxy.list_processes()

    return jsonify(processes)

@app.route('/process/<string:name>', methods=['GET'])
def process_metrics(name):
    with ServerProxy(url) as proxy:
        process_metrics = proxy.get_metrics(name)

    return jsonify(process_metrics)

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', 8080)