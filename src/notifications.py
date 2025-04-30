import time 
from datetime import datetime
from flask import Response

from app import app 

@app.route('/stream')
def stream():

    def get_data():

        while True:
            #gotcha
            time.sleep(1)
            yield f'data: {datetime.now().second} \n\n'

    return Response(get_data(), mimetype='text/event-stream')
