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
    notices = db.collection('notices')
    ordered_notices = notices.order_by('updated_at', direction='DESCENDING')
    results = []
    for notice in ordered_notices.stream():
        item = notice.to_dict()
        item['id'] = notice.id
        item['timestamp'] = str(item['updated_at'])[:16]
        results.append(item)
    return results


def save_notice(email, title, description):
    db = firestore.Client()
    right_now = datetime.now()
    notices = db.collection('notices').add({
        'email': email,
        'title': title,
        'description': description,
        'created_at': right_now,
        'updated_at': right_now
    })


def replace_notice(id, title, description):
    db = firestore.Client()
    right_now = datetime.now()
    notice = db.collection('notices').document(document_id=id)
    if notice is None:
        return None

    notice.set({
        'title': title,
        'description': description,
        'updated_at': right_now
    }, merge=True)


def get_notice(id):
    db = firestore.Client()
    doc = db.collection('notices').document(document_id=id)

    if doc is None:
        return None
    req = doc.get()
    if not req.exists:
        return None

    notice = req.to_dict()
    notice['id'] = id
    return notice


@app.route('/', methods=['GET'])
def home_page():
    public_url = os.environ.get('public')
    return render_template('homepage.html', public=public_url,
        email=get_email(), notices=list_notices())


@app.route('/new-notice', methods=['POST'])
def create_notice():
    title = request.form.get('title')
    description = request.form.get('description')
    email = get_email()
    
    save_notice(email, title, description)
    return redirect('/')


@app.route('/replace-notice', methods=['POST'])
def update_notice():
    title = request.form.get('title')
    description = request.form.get('description')
    id = request.form.get('id')
    
    replace_notice(id, title, description)
    return redirect('/')


@app.route('/view-notice/<id>')
def view_notice(id):
    public_url = os.environ.get('public')
    info = get_notice(id)
    if info is None:
        return 'No such request', 404
    return render_template('view-notice.html',
        public=public_url, notice=info)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
