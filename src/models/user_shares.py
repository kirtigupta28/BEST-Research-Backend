from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/yourdatabase"  # Your MongoDB URI
mongo = PyMongo(app)

class UserSharesModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.user_shares  # Assuming the collection is named 'user_shares'

    def create_user_share(self, uid, public_key, share_of_public_key):
        """
        Create a new user share entry.
        :param uid: User ID
        :param public_key: Public key of the user
        :param share_of_public_key: Share of the user's public key
        :return: Inserted document ID as a string
        """
        share_data = {
            "UID": uid,
            "PublicKey": public_key,
            "ShareOfPublicKey": share_of_public_key
        }
        result = self.collection.insert_one(share_data)
        return str(result.inserted_id)

    def find_share_by_uid(self, uid):
        """
        Find user share by UID.
        :param uid: User ID to search for
        :return: Document with user share details or None
        """
        return self.collection.find_one({"UID": uid})

    def update_user_share(self, uid, public_key, share_of_public_key):
        """
        Update share details for a specific User ID.
        :param uid: User ID to identify the record
        :param public_key: New public key
        :param share_of_public_key: New share of the public key
        :return: True if update succeeded, False otherwise
        """
        result = self.collection.update_one(
            {"UID": uid},
            {"$set": {"PublicKey": public_key, "ShareOfPublicKey": share_of_public_key}}
        )
        return result.modified_count > 0

    def delete_user_share(self, uid):
        """
        Delete a user share entry by UID.
        :param uid: User ID of the record to delete
        :return: True if deletion succeeded, False otherwise
        """
        result = self.collection.delete_one({"UID": uid})
        return result.deleted_count > 0

    def get_all_user_shares(self):
        """
        Get all user shares in the collection.
        :return: List of all documents in the collection
        """
        return list(self.collection.find({}, {"_id": 0}))  # Excludes the MongoDB `_id` field


# Initialize the UserSharesModel
user_shares_model = UserSharesModel(mongo.db)


@app.route("/user_share", methods=["POST"])
def create_user_share():
    """
    API endpoint to create a new user share entry.
    Expects JSON body with keys: UID, PublicKey, ShareOfPublicKey
    """
    data = request.json
    try:
        share_id = user_shares_model.create_user_share(
            uid=data["UID"],
            public_key=data["PublicKey"],
            share_of_public_key=data["ShareOfPublicKey"]
        )
        return jsonify({"message": "User Share created successfully", "share_id": share_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/user_share/<uid>", methods=["GET"])
def get_user_share(uid):
    """
    API endpoint to retrieve user share details by UID.
    """
    share_data = user_shares_model.find_share_by_uid(uid)
    if share_data:
        return jsonify(share_data), 200
    return jsonify({"error": "User Share not found"}), 404


@app.route("/user_share/<uid>", methods=["PUT"])
def update_user_share(uid):
    """
    API endpoint to update the user share for a specific UID.
    Expects JSON body with the new PublicKey and ShareOfPublicKey.
    """
    data = request.json
    success = user_shares_model.update_user_share(uid, data["PublicKey"], data["ShareOfPublicKey"])
    if success:
        return jsonify({"message": "User Share updated successfully"}), 200
    return jsonify({"error": "Failed to update user share"}), 400


@app.route("/user_share/<uid>", methods=["DELETE"])
def delete_user_share(uid):
    """
    API endpoint to delete a user share entry by UID.
    """
    success = user_shares_model.delete_user_share(uid)
    if success:
        return jsonify({"message": "User Share deleted successfully"}), 200
    return jsonify({"error": "User Share not found"}), 404

@app.route("/public_key_shares/<public_key>", methods=["GET"])
def get_shares_by_public_key(public_key):
    """
    API endpoint to retrieve all shares associated with a specific PublicKey.
    :param public_key: Public key to search for
    :return: JSON response with all matching shares or an error message
    """
    try:
        shares = list(user_shares_model.collection.find({"PublicKey": public_key}, {"_id": 0}))
        if shares:
            return jsonify({"PublicKey": public_key, "Shares": shares}), 200
        return jsonify({"error": "No shares found for the given public key"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/user_share", methods=["GET"])
def get_all_user_shares():
    """
    API endpoint to retrieve all user share entries.
    """
    all_shares = user_shares_model.get_all_user_shares()
    return jsonify(all_shares), 200


if __name__ == "__main__":
    app.run(debug=True)
