from firebase_admin import initialize_app
from firebase_admin import getDatabase, ref, set, get, child
from flask import Flask, request
from app import app

default_app = initialize_app()

# Your web app's Firebase configuration
firebaseConfig = {
  "apiKey": "AIzaSyDghhvb9t2ZjcC65hLoH8aGNKpSIPzp8N0",
  "authDomain": "tess-research.firebaseapp.com",
  "projectId": "tess-research",
  "storageBucket": "tess-research.firebasestorage.app",
  "messagingSenderId": "694576180227",
  "appId": "1:694576180227:web:684d6f7098408f9ec5b236"
}

# Initialize Firebase
_ = initialize_app(firebaseConfig)
firebase_db = getDatabase()
firebase_db_ref = ref(firebase_db)

def saveToken(userId: str, token: str):
  values = get(child(firebase_db_ref, f"userTokens/{userId}/")).val() or {}
  payload = {**values, "token": token}
  set(ref(firebase_db, f"userTokens/{userId}/"), payload)


@app.route("/registerPushToken", methods=["POST"])
def registerPushToken ():
  userId = request.json.get("userId")
  token = request.json.get("token")
  saveToken(userId, token)
  return "success", 200
