from app import app, db
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user

class Keys: 
    def __init__(self, db): 
        self.__collection__ = db.keys

    def create(self, data, user_id):
        """
        Creates a new key entry for a user.
        
        PARAMS
        ------
        user_id: (str) The ID of the user.
        key_data: (str/ hex) The public key of user

        RETURNS
        -------
        result: (str) The ID of the inserted key document.
        """
        #check if already exists
        res = self.get_by_user_id(user_id)
        if res: 
            return None
        result = self.__collection__.insert_one({
            "user_id": user_id,
            "key_data": data["key_data"]
        })
        return str(result.inserted_id)

    def get_by_user_id(self, user_id):
        """
        Retrieves a key entry by user ID.

        PARAMS
        ------
        user_id: (str) The ID of the user.

        RETURNS
        -------
        key_entry: (dict) The key entry associated with the user ID.
        """
        res = self.__collection__.find_one({"user_id": user_id}, {"_id": 0})
        if res:
            return res
        return None

# Initialize the Keys model
keys_model = Keys(db)

# Routes
@app.route("/api/keys", methods=["POST"])
@jwt_required()
def create_key():
    """API to create a new key for a user"""
    data = request.json
    if not data or "key_data" not in data:
        return jsonify({"error": "Invalid request"}), 400

    key_id = keys_model.create(data, user_id=current_user.get("_id"))
    if not key_id:
        return jsonify({"error": "Key already exists"}), 400
    return jsonify({"message": "Key created", "key_id": key_id}), 201


@app.route("/api/keys", methods=["GET"])
# @jwt_required
def get_key_by_user_id():
    """API to retrieve a key by user ID"""
    key_entry = keys_model.get_by_user_id(user_id)
    if not key_entry:
        return jsonify({"error": "Key not found"}), 404

    return jsonify(key_entry), 200

@app.route("/api/keys/exists", methods=["GET"])
@jwt_required()
def check_key_exists(): 
    user_id = current_user.get("_id")
    key_entry = keys_model.get_by_user_id(user_id)
    if not key_entry:
        return jsonify({"exists": False}), 404
    return jsonify({"exists": True}), 200