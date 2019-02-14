from flask import Flask , Response
from xmlrpc.client import ServerProxy
import json

url = 'http://localhost:8000/process-manager'

app = Flask(__name__, static_folder='./static/', static_url_path='/static')

@app.route('/list', methods=['GET'])
def list():
    with ServerProxy(url) as proxy:
        processes = proxy.list_processes()
    return Response(json.dumps(processes), 200, content_type='application/json')

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', 8080)