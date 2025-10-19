import base64
import json
import logging
import os
import sys
import requests
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from pprint import pformat

app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(streamhandler := logging.StreamHandler(sys.stdout))
streamhandler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
logger.debug("DEBUG logging is enabled")
logger.info("INFO logging is enabled")
logger.warning("WARNING logging is enabled")
logger.error("ERROR logging is enabled")
logger.fatal("FATAL logging is enabled")


@app.route('/')
def index():
    print('Request for index page received')
    print(pformat((request,)))#, dict(request.headers), dict(os.environ))))
    for header, value in request.headers.items():
        try:
            value = base64.b64decode(value).decode('utf-8')
        except:
            try:
                # JWT token?
                value = base64.b64decode(value.split(".")[1]).decode("utf-8")
            except:
                pass
        try:
            value = json.loads(value)
        except:
            pass
        print(pformat((header, value)))

    try:
        user_token = request.headers.get("X-MS-TOKEN-AAD-ACCESS-TOKEN", "")
        print("User token: "+user_token)
        user_groups = fetchUserGroups(user_token)
        print(f"User is member of {len(user_groups)} groups")
        for group in user_groups:
            print(f"  Group: {group!r}")
    except:
        logger.exception("Error fetching user groups")
    return render_template('index.html')


def fetchUserGroups(userToken, nextLink=None):
    # Recursively fetch group membership
    if nextLink:
        endpoint = nextLink
    else:
        endpoint = "https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$select=id"

    headers = {"Authorization": "bearer " + userToken}
    try:
        r = requests.get(endpoint, headers=headers)
        if r.status_code != 200:
            logging.error(f"Error fetching user groups: {r.status_code} {r.text}")
            return []

        r = r.json()
        if "@odata.nextLink" in r:
            nextLinkData = fetchUserGroups(userToken, r["@odata.nextLink"])
            r["value"].extend(nextLinkData)

        return r["value"]
    except Exception as e:
        logging.error(f"Exception in fetchUserGroups: {e}")
        return []


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
