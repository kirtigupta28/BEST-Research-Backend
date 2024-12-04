from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app import app,db
from pymongo.collection import Collection
from .user import get_all_admin
class UserSharesModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection: Collection = db.user_shares

      
    def create_user_share(self, user_id, public_key):
        """
        Creates a new user share entry.
        :param user_id: User's MongoDB generated ID
        :param public_key: Public key of the user
        :return: Inserted document ID
        """
        share_data = {
            "user_id": ObjectId(user_id),
              # MongoDB ObjectId of the user
            "public_key": public_key
        }

        result = self.collection.insert_one(share_data)
        return str(result.inserted_id)

    
    def find_share_by_user_id(self, user_id):
        """
        Finds a user share by the UserID.
        :param user_id: MongoDB ObjectId of the user
        :return: User share document or None
        """
        try:
            object_id = ObjectId(user_id)
            res = self.collection.find_one({"user_id": object_id}, {"_id": 0, "public_key": 1})
            if(res == None):
                return {"data" : False}
            else:
                return {"data" : True}
            # return res
        except Exception as e:
            return None


    def delete_user_share(self, share_id):
        """
        Delete a user share entry by MongoDB-generated _id.
        :param share_id: The MongoDB ObjectId as a string
        :return: True if deletion succeeded, False otherwise
        """
        try:
            # Convert the string ID to an ObjectId
            object_id = ObjectId(share_id)
            # Perform the delete operation
            result = self.collection.delete_one({"_id": object_id})
            # Check if a document was deleted
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting share by ID: {e}")
            return False



    def get_all_user_shares(self):
        """
        Get all user shares with their _id and PublicKey.
        :return: List of dictionaries containing _id and PublicKey for all documents in the collection
        """
        return list(
            self.collection.find({}, {"_id": 0, "PublicKey": 1})  # Include only _id and PublicKey fields
        )



# Initialize the UserSharesModel
user_shares_model = UserSharesModel(db)



@app.route("/api/usershare", methods=["POST"])
def create_user_share():
    """
    API endpoint to create a new user share entry.
    Expects JSON body with keys: UID, PublicKey
    """
    data = request.json
    try:
        # Ensure all required fields are provided
        if not all(key in data for key in ("user_id", "public_key")):
            return jsonify({"error": "Missing required fields"}), 400
        
        # # Check if the user already has a public key
        # existing_share = user_shares_model.find_share_by_user_id(data["user_id"])
        # if existing_share:
        #     # console.log("key exists");
        #     return jsonify({"error": "Public key already exists for this user"}), 400
        
        # Create user share without ShareOfPublicKey
        share_id = user_shares_model.create_user_share(
            user_id=data["user_id"],
            public_key=data["public_key"]
        )
        return jsonify({"message": "User Share created successfully", "share_id": share_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/user_share/<string:uid>", methods=["GET"])
def get_user_share(uid):
    """
    API endpoint to retrieve user share details by UID.
    """
    try:
        # Retrieve user share by UID
        share_data = user_shares_model.find_share_by_user_id(uid)
        return jsonify(share_data)
        # if share_data:
            
        #     # return jsonify(share_data), 200
        #     return jsonify({'data' : True}),200
        # return jsonify({'data' : False}),404
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/usershare", methods=["GET"])
def get_all_user_shares():
    """
    API endpoint to retrieve all user share entries.
    """
    try:
        # Fetch all user shares
        all_shares = user_shares_model.get_all_user_shares()
        print (all_shares)
        return all_shares, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
def get_all_admin_key_shares(): 
    '''Returns all admin users'''
    list_of_admins = get_all_admin()
    list_of_admin_key_shares = []
    for admin in list_of_admins:
        pubKeyShare = user_shares_model.collection.find_one({"user_id": admin.get("_id")}, {"_id": 0, "public_key": 1})
        print(pubKeyShare)
        # error here pubKeyShare is None
        if(pubKeyShare["data"]):
            list_of_admin_key_shares.append(admin)
    return list_of_admin_key_shares


# # if _name_ == "_main_":
#     app.run(debug=True)