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

    def update_user_share(self, uid, updates):
        """
        Update share details for a specific User ID.
        :param uid: User ID to identify the record
        :param updates: Dictionary of fields to update
        :return: True if update succeeded, False otherwise
        """
        result = self.collection.update_one({"UID": uid}, {"$set": updates})
        return result.modified_count > 0

    def delete_user_share(self, uid):
        """
        Delete a user share by UID.
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
