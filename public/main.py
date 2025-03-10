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


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home_page():
    support_url = os.environ.get('support')
    return render_template('homepage.html', support=support_url)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    