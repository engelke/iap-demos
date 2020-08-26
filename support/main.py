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


def list_requests():
    db = firestore.Client()
    docs_query = db.collection('requests').where('email', '==', get_email())
    ordered_docs_query = docs_query.order_by('updated_at', direction='DESCENDING')
    results = []
    for doc in ordered_docs_query.stream():
        item = doc.to_dict()
        item['id'] = doc.id
        item['timestamp'] = str(item['updated_at'])[:16]
        results.append(item)
    return results


def save_request(email, title, description):
    db = firestore.Client()
    right_now = datetime.now()
    requests = db.collection('requests').add({
        'email': email,
        'title': title,
        'description': description,
        'created_at': right_now,
        'updated_at': right_now
    })


@app.route('/', methods=['GET'])
def home_page():
    public_url = os.environ.get('public')
    return render_template('homepage.html', public=public_url,
        email=get_email(), requests=list_requests())


@app.route('/new-request', methods=['POST'])
def create_request():
    title = request.form.get('title')
    description = request.form.get('description')
    email = get_email()
    
    save_request(email, title, description)

    return redirect('/')
    pass


@app.route('/new-comment', methods=['POST'])
def add_comment():
    pass
