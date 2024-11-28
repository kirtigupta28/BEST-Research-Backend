class UserPolyModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.user_poly_values  # Assuming the collection is named 'user_poly_values'

    def create_user_poly(self, uid, poly_values):
        """
        Create a new user with polynomial values.
        :param uid: User ID
        :param poly_values: Array of polynomial values
        :return: Inserted document ID as a string
        """
        data = {
            "UID": uid,
            "PolyValues": poly_values
        }
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def find_user_poly_by_uid(self, uid):
        """
        Find polynomial values by User ID.
        :param uid: User ID to search for
        :return: Document with polynomial values or None
        """
        return self.collection.find_one({"UID": uid})

    def update_user_poly(self, uid, poly_values):
        """
        Update polynomial values for a specific User ID.
        :param uid: User ID
        :param poly_values: New array of polynomial values
        :return: True if update succeeded, False otherwise
        """
        result = self.collection.update_one({"UID": uid}, {"$set": {"PolyValues": poly_values}})
        return result.modified_count > 0

    def delete_user_poly(self, uid):
        """
        Delete polynomial values for a specific User ID.
        :param uid: User ID
        :return: True if deletion succeeded, False otherwise
        """
        result = self.collection.delete_one({"UID": uid})
        return result.deleted_count > 0

    def get_all_user_polys(self):
        """
        Get all user polynomial entries.
        :return: List of all documents in the collection
        """
        return list(self.collection.find({}, {"_id": 0}))  # Excludes the MongoDB `_id` field
