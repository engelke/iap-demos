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
    docs_query = db.collection('requests')
    ordered_docs_query = docs_query.order_by('updated_at', direction='DESCENDING')
    results = []
    for doc in ordered_docs_query.stream():
        item = doc.to_dict()
        item['id'] = doc.id
        item['timestamp'] = str(item['updated_at'])[:16]
        results.append(item)
    return results


def get_request(id):
    db = firestore.Client()
    doc = db.collection('requests').document(document_id=id)

    if doc is None:
        return None
    req = doc.get()
    if not req.exists:
        return None

    info = req.to_dict()
    info['id'] = id

    comments = doc.collection('comments').stream()
    print('comments collection is {}'.format(comments))
    info['comments'] = []
    for comment in comments:
        item = comment.to_dict()
        item['created_at'] = str(item['created_at'])[:16]
        info['comments'].append(item)
    return info


def save_comment(email, request_id, comment):
    db = firestore.Client()
    doc = db.collection('requests').document(document_id=request_id)

    if doc is None:
        return None
    req = doc.get()
    if not req.exists:
        return None

    info = req.to_dict()

    right_now = datetime.now()
    requests = doc.collection('comments').add({
        'comment': comment,
        'commenter': get_email(),
        'created_at': right_now,
        'updated_at': right_now
    })

    doc.set({'updated_at': right_now}, merge=True)
    return True


@app.route('/', methods=['GET'])
def home_page():
    public_url = os.environ.get('public')
    return render_template('homepage.html', public=public_url,
        requests=list_requests())


@app.route('/view-request/<id>')
def view_request(id):
    public_url = os.environ.get('public')
    info = get_request(id)
    if info is None:
        return 'No such request', 404
    return render_template('view-request.html',
        public=public_url, request=info)


@app.route('/new-comment', methods=['POST'])
def add_comment():
    id = request.form.get('id')
    comment = request.form.get('comment')
    email = get_email()
    
    if save_comment(email, id, comment) is not None:
        return redirect('/view-request/{}'.format(id))
    else:
        return 'Save failed', 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
