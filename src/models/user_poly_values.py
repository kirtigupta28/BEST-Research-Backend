from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from app import app, db
from bson import ObjectId
from .user import get_all_admin

class UserPolyModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.user_poly_values  # Assuming the collection is named 'user_poly_values'

    def create_user_poly(self, uid, polyvalues):
        """
        Create a new user entry with poly values.
        :param uid: User ID
        :param poly_values: Array of polynomial values
        :return: Inserted document ID as a string
        """
        user_data = {
            "uid": ObjectId(uid),
            "polyvalues": polyvalues
        }
        # print(user_data)
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def get_user_poly(self, uid):
        """
        Find user poly values by UID.
        :param uid: User ID
        :return: Document with user poly values or None
        """
        return self.collection.find_one({"uid": uid}, {"_id": 0, "uid": 0})

    def update_user_poly(self, uid, polyvalues):
        """
        Update the poly values for a specific UID.
        :param uid: User ID to identify the record
        :param poly_values: New array of poly values
        :return: True if update succeeded, False otherwise
        """
        result = self.collection.update_one({"uid": ObjectId(uid)}, {"$set": {"polyvalues": polyvalues}})
        return result.modified_count > 0

    def delete_user_poly(self, uid):
        """
        Delete a user poly entry by UID.
        :param uid: User ID of the record to delete
        :return: True if deletion succeeded, False otherwise
        """
        result = self.collection.delete_one({"uid": ObjectId(uid)})
        return result.deleted_count > 0


# Initialize the UserPolyModel
user_poly_model = UserPolyModel(db)

@app.route("/api/userpoly", methods=["POST"])
def create_user_poly():
    """
    API endpoint to create a new user poly entry.
    Expects JSON body with keys: UID and PolyValues
    """
    data = request.json
    try:      
        user_id = user_poly_model.create_user_poly(
            uid=data["uid"],
            polyvalues=data["polyvalues"]
        )
        return jsonify({"message": "User Poly created successfully", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/user_poly_vals/<string:uid>", methods=["GET"])
def get_user_poly(uid):
    """
    API endpoint to retrieve poly values by UID.
    """
    user_data = user_poly_model.get_user_poly(ObjectId(uid))
    if user_data:
        return user_data, 200
    return jsonify({"error": "User not found"}), 404


@app.route("/api/user_poly/<string:uid>", methods=["PUT"])
def update_user_poly(uid):
    """
    API endpoint to update the poly values for a specific UID.
    Expects JSON body with the new PolyValues array.
    """
    data = request.json
    success = user_poly_model.update_user_poly(ObjectId(uid), data["polyvalues"])
    if success:
        return jsonify({"message": "User Poly updated successfully"}), 200
    return jsonify({"error": "Failed to update user poly"}), 400


@app.route("/api/userpoly/<string:uid>", methods=["DELETE"])
def delete_user_poly(uid):
    """
    API endpoint to delete a user poly entry by UID.
    """
    success = user_poly_model.delete_user_poly(ObjectId(uid))
    if success:
        return jsonify({"message": "User Poly deleted successfully"}), 200
    return jsonify({"error": "User not found"}), 404


@app.route("/api/admins", methods=["GET"])
def fetch_all_admin():
    '''Returns all admin users'''
    try:
        admins = get_all_admin()  # Call the function to fetch admin users
        return jsonify(admins), 200  # Return as a JSON response
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle exceptions

@app.route("/api/get_combined_shares", methods=["GET"])
def get_combined_shares():
    """
    Endpoint to get combined polynomial shares from all users based on sorted order.
    """
    try:
        # Step 1: Fetch sorted admin users
        admins = get_all_admin()  # This returns an array of user_ids in sorted order
        user_shares = []

        # Step 2: For each admin, retrieve their polynomial values based on their position in the sorted list
        for admin in admins:
            user_poly = user_poly_model.get_user_poly(admin["user_id"])  # Get their poly values from DB
            if user_poly:
                user_shares.append(user_poly["polyvalues"])

        # Step 3: Combine shares based on position
        combined_shares = []
        for i in range(len(user_shares[0])):  # Assuming all users have the same number of shares
            total = sum(int(share[i]) for share in user_shares)
            combined_shares.append(str(total))  # Convert the sum to string before sending as response

        return jsonify({"combined_shares": combined_shares}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "main":
    app.run(debug=True)