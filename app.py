import base64
import json
import logging
import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from pprint import pformat

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    print('Request for index page received')
    print(pformat((request, dict(request.headers), dict(os.environ))))
    for header, value in request.headers.items():
        try:
            value = base64.b64decode(value)
        except:
            pass
        try:
            value = value.decode('utf-8')
        except:
            pass
        try:
            value = json.loads(value)
        except:
            pass
        print(pformat((header, value)))
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')

    if name:
        print('Request for hello page received with name=%s' % name)
        return render_template('hello.html', name=name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
