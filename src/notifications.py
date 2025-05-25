import time 
from datetime import datetime
from flask import Response, request, jsonify

from app import app 

main_data = {}

@app.route('/stream')
def stream():

    def get_data():
        global main_data

        while True:
            #gotcha
            # time.sleep(1)
            # yield f'data: {datetime.now().second} \n\n'
            if main_data.get("key", None):
                key_data = main_data.get("key")
                main_data = {}
                yield f'data: {key_data}\n\n'

    return Response(get_data(), mimetype='text/event-stream')


@app.route('/recieve-data', methods=["POST"])
def receive_data(): 
    global main_data
    data = request.json
    if data.get("key", None): 
        # then set data and send this data to the browser
        main_data = {"key": data.get("key")}
        return jsonify({"message": "Created"}), 201

    return jsonify({"message": "Send some data"}), 400

