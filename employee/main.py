# Copyright 2020 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import os

from flask import Flask, redirect, render_template, request
from google.cloud import firestore


app = Flask(__name__)


def get_email():
    authenticated_email = request.headers.get('X-Goog-Authenticated-User-Email', '')
    if authenticated_email.startswith('accounts.google.com:'):
        return authenticated_email[20:]
    else:
        return authenticated_email


def list_notices():
    db = firestore.Client()
    docs_query = db.collection('notices')
    #ordered_docs_query = docs_query.order_by('updated_at', direction='DESCENDING')
    results = []
    for doc in docs_query.stream():
        item = doc.to_dict()
        item['timestamp'] = str(item['updated_at'])[:16]
        results.append(item)
    return results


@app.route('/', methods=['GET'])
def home_page():
    public_url = os.environ.get('public')
    return render_template('homepage.html', public=public_url,
        email=get_email(), notices=list_notices())


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
