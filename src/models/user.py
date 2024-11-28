from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.users  # Assuming the collection is named 'users'

    def create_user(self, email, password, is_admin_faculty, name):
        """
        Create a new user.
        :param email: User's email
        :param password: Plaintext password
        :param is_admin_faculty: Boolean for admin/faculty status
        :param name: User's name
        :return: Inserted user ID as a string
        """
        hashed_password = generate_password_hash(password)
        user_data = {
            "Email": email,
            "Password": hashed_password,
            "isAdmin_Faculty": is_admin_faculty,
            "Name": name
        }
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def find_user_by_email(self, email):
        """
        Find a user by email.
        :param email: Email to search for
        :return: User document or None
        """
        return self.collection.find_one({"Email": email})

    def verify_password(self, email, password):
        """
        Verify a user's password.
        :param email: User's email
        :param password: Plaintext password
        :return: True if valid, False otherwise
        """
        user = self.find_user_by_email(email)
        if user and check_password_hash(user["Password"], password):
            return True
        return False

    def update_user(self, email, updates):
        """
        Update user details.
        :param email: User's email to identify the user
        :param updates: Dictionary of fields to update
        :return: True if update succeeded, False otherwise
        """
        result = self.collection.update_one({"Email": email}, {"$set": updates})
        return result.modified_count > 0

    def delete_user(self, email):
        """
        Delete a user by email.
        :param email: User's email
        :return: True if deletion succeeded, False otherwise
        """
        result = self.collection.delete_one({"Email": email})
        return result.deleted_count > 0

    def get_all_users(self):
        """
        Get all users.
        :return: List of all user documents
        """
        return list(self.collection.find({}, {"_id": 0}))  # Excludes the MongoDB `_id` field
