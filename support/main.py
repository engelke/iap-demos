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

import os

from flask import Flask, make_response, render_template, request
from google.cloud import firestore


app = Flask(__name__)


def get_email():
    authenticated_email = request.headers.get('X-Goog-Authenticated-User-Email', '')
    if authenticated_email.startswith('accounts.google.com:'):
        return authenticated_email[20:]
    else:
        return authenticated_email


def list_requests():
    db = firestore.Client()
    docs = db.collection('requests').where('email', '==', get_email()).stream()
    results = []
    for doc in docs:
        results.append(doc.to_dict())
    return results


@app.route('/', methods=['GET'])
def home_page():
    public_url = os.environ.get('public')
    return render_template('homepage.html', public=public_url,
        requests=list_requests())
    