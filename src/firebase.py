import firebase_admin
from firebase_admin import credentials, db, firestore
from datetime import datetime
from app import app
from flask import request, jsonify
from exponent_server_sdk import PushClient, PushMessage
from dotenv import dotenv_values

secrets = dotenv_values('.env')

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("./data.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': secrets["FIREBASE_URI"]
    })

@app.route('/send_data', methods=['POST'])
def send_data():
    try:
        # Extract data from the request body
        data = request.json
        user_id = data.get('user_id')
        token = data.get('token')

        if not user_id or token is None:
            return jsonify({"error": "Invalid input"}), 400

        # Save data to Firebase
        ref = db.reference(f'users/{user_id}')
        ref.set({'token': token})

        return jsonify({"message": "Data sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get data from Firebase Realtime Database
@app.route('/get_data/<user_id>', methods=['POST'])
def get_data(user_id):
    try:
        # Get data from Firebase
        ref = db.reference(f'users/{user_id}')
        data = ref.get()

        if not data:
            return jsonify({"message": "No data found for the user"}), 404

        # Extract token
        token = data.get('token')

        push_client = PushClient()
        push_message = PushMessage(
            to=token,
            title="Important for examination process!",
            body="Login into the app to generate your polynomial values!"
        )
        push_client.publish(push_message)

        return jsonify({"message": "Notification sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# # Save token for a user
# @app.route("/api/savetoken", methods=["POST"])
# def save_token():
#     data = request.json
#     if data: 
#         # push data into db
#         doc_ref = db.collection('userTokens').document()
#         doc_ref.set(data)
#         return jsonify({"id"}), 201
#     else:
#         return jsonify({"error": "Request body must be JSON"}), 400
#     # ref = db.reference(f"userTokens/{user_id}")
#     # current_values = ref.get() or {}
#     # current_values['token'] = token
#     # ref.set(current_values)

# # Get token for a user
# def get_token(user_id):
#     ref = db.reference(f"userTokens/{user_id}")
#     return ref.get() or {}

# Save moisture level sample
# def save_sample(moisture_level, user_id):
#     timestamp = datetime.now().timestamp()
#     ref = db.reference(f"users/{user_id}/{int(timestamp)}")
#     ref.set({'moisture': moisture_level})

# Get moisture level samples
# def get_samples(user_id):
#     ref = db.reference(f"users/{user_id}")
#     values = ref.get()
#     if not values:
#         return {
#             "currentMoistureLevel": None,
#             "previousMoistureLevels": []
#         }
    
#     moisture_readings = [entry['moisture'] for entry in values.values()]
#     return {
#         "currentMoistureLevel": moisture_readings[-1],
#         "previousMoistureLevels": moisture_readings
#     }
