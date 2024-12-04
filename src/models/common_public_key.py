from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app import app,db
from pymongo.collection import Collection
from .user_shares import get_all_admin_key_shares
from ..utils import compute_overall_public_key, hex_to_point

class CommonPubkeyModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection: Collection = db.common_public_keys

    def create_common_public_key(self):
        list_of_admin_shares = get_all_admin_key_shares()
        list_of_pub_keys = []

        #convert the public keys to points
        for share in list_of_admin_shares:
            list_of_pub_keys.append(hex_to_point(share["public_key"]))

        print(list_of_admin_shares)

        Q = compute_overall_public_key(list_of_pub_keys)

        public_key = {
            "common_public_key": Q
        }

        result = self.collection.insert_one(public_key)
        return str(result.inserted_id)


    def get_common_public_key(self):
        """
        Get all user shares with their _id and PublicKey.
        :return: List of dictionaries containing _id and PublicKey for all documents in the collection
        """
        try:
            response = self.collection.find_one({}, {"_id": 0, "common_public_key": 1})
            print(response)
            return response
        except Exception as e:
            return None


common_public_key_model = CommonPubkeyModel(db)


def get_common_public_key():
    return common_public_key_model.get_common_public_key()


@app.route('/api/common_public_key', methods=['POST'])
def create_common_public_key():
    return common_public_key_model.create_common_public_key()