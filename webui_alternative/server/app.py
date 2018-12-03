# Copyright 2017 Bo Shao. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
import tensorflow as tf
import firebase_admin
import time
import json

from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, request, jsonify
from settings import PROJECT_ROOT
from chatbot.botpredictor import BotPredictor

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
app = Flask(__name__)

@app.route('/reply', methods=['POST', 'GET'])
def reply():
#    user_id = request.args.get('userID')
#    question = request.args.get('question')
    session_id = 1
    data = json.loads(request.get_data(as_text=True))
    print(data)
    user_id = data['userID']
    question = data['message']
    if user_id not in predictor.session_data.id_dict:  # Including the case of 0
        session_id = predictor.session_data.add_session(user_id)
    else:
        session_id = predictor.session_data.id_dict[user_id]
#    print(session_id, question)
    answer = predictor.predict(session_id, question)
    ref = db.reference('messages')
    ref2 = ref.child(user_id)
    ref3 = ref2.child('messages')
    ref3.push().set(
        {
        'content' : answer,
        'data' : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'user' : 'Tok'
    })
    return answer
#    return jsonify({'sessionId': session_id, 'sentence': answer})


if __name__ == "__main__":
    cred = credentials.Certificate('key2.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://uci-tok.firebaseio.com'
    })

    corp_dir = os.path.join(PROJECT_ROOT, 'Data', 'Corpus')
    knbs_dir = os.path.join(PROJECT_ROOT, 'Data', 'KnowledgeBase')
    res_dir = os.path.join(PROJECT_ROOT, 'Data', 'Result')

    with tf.Session() as sess:
        predictor = BotPredictor(sess, corpus_dir=corp_dir, knbase_dir=knbs_dir,
                                 result_dir=res_dir, result_file='basic')

        app.run(port=5000)
        print("Web service started.")
