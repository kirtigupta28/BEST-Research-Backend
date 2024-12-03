from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app and MongoDB
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/yourdatabase"
mongo = PyMongo(app)

# User Model
class UserModel:
    def __init__(self):
        self.collection = mongo.db.users  # Assuming the collection is named 'users'

    # http://localhost:5000/api/users/register
    @app.route("/register", methods=["POST"])
    def create_user(self, email, password, is_admin_faculty, name):
        """Creates a new user"""
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
        """Finds a user by email"""
        return self.collection.find_one({"Email": email})

    def verify_password(self, email, password):
        """Verifies the password for a given email"""
        user = self.find_user_by_email(email)
        if user and check_password_hash(user["Password"], password):
            return True
        return False

    def update_user(self, email, updates):
        """Updates user data"""
        result = self.collection.update_one({"Email": email}, {"$set": updates})
        return result.modified_count > 0

    def delete_user(self, email):
        """Deletes a user by email"""
        result = self.collection.delete_one({"Email": email})
        return result.deleted_count > 0

    @app.route("/", methods=["GET"])
    def get_all_users(self):
        """Returns all users"""
        return list(self.collection.find({}, {"_id": 0}))  # Excluding MongoDB `_id`

# Example usage
if __name__ == "__main__":
    with app.app_context():
        user_model = UserModel()
        
        # Create a user
        user_model.create_user("john.doe@example.com", "securepassword", True, "John Doe")
        
        # Find a user
        user = user_model.find_user_by_email("john.doe@example.com")
        print(user)
        
        # Verify password
        is_valid = user_model.verify_password("john.doe@example.com", "securepassword")
        print("Password valid:", is_valid)
