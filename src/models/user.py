# from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
# # from dotenv import load_dotenv
# # import os
# from app import app, db

# # Load environment variables from the .env file/
# # load_dotenv()

# # Initialize Flask app
# # app = Flask(_name_)

# # # MongoDB Configuration
# # mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/yourdatabase")
# # app.config["MONGO_URI"] = mongo_uri
# # mongo = PyMongo(app)

# # User Model
# class UserModel:
#     def __init__(self, db):
#         self.collection = db.users  # Assuming the collection is named 'users'

#     def create_user(self, email, password, is_admin, name):
#         """Creates a new user"""
#         hashed_password = generate_password_hash(password)
#         user_data = {
#             "Email": email,
#             "Password": hashed_password,
#             "isAdmin": is_admin,
#             "Name": name
#         }
#         result = self.collection.insert_one(user_data)
#         return str(result.inserted_id)

#     def find_user_by_email(self, email):
#         """Finds a user by email"""
#         return self.collection.find_one({"Email": email})

#     def verify_password(self, email, password):
#         """Verifies the password for a given email"""
#         user = self.find_user_by_email(email)
#         if user and check_password_hash(user["Password"], password):
#             return True
#         return False

#     def update_user(self, email, updates):
#         """Updates user data"""
#         result = self.collection.update_one({"Email": email}, {"$set": updates})
#         return result.modified_count > 0

#     def delete_user(self, email):
#         """Deletes a user by email"""
#         result = self.collection.delete_one({"Email": email})
#         return result.deleted_count > 0

#     def get_all_users(self):
#         """Returns all users"""
#         return list(self.collection.find({}, {"_id": 0}))  # Excluding MongoDB _id

# # Initialize UserModel
# user_model = UserModel(db)

# # Routes
# @app.route("/api/users/register", methods=["POST"])
# def register_user():
#     """API to register a new user"""
#     data = request.json
#     if not data:
#         return jsonify({"error": "Invalid request"}), 400

#     email = data.get("email")
#     password = data.get("password")
#     is_admin = data.get("is_admin", False)
#     name = data.get("name")

#     if not all([email, password, name]):
#         return jsonify({"error": "Missing required fields"}), 400

#     user_id = user_model.create_user(email, password, is_admin, name)
#     return jsonify({"message": "User created", "user_id": user_id}), 201

# @app.route("/api/users", methods=["GET"])
# def get_users():
#     """API to fetch all users"""
#     users = user_model.get_all_users()
#     return jsonify(users), 200

# @app.route("/api/users/admin", methods=["GET"])
# def get_admin():
#     """API to fetch all admin users"""
#     admin = user_model.get_all_admin()
#     return jsonify(admin), 200

# @app.route("/api/users/<email>", methods=["DELETE"])
# def delete_user(email):
#     """API to delete a user by email"""
#     if user_model.delete_user(email):
#         return jsonify({"message": f"User with email {email} deleted"}), 200
#     return jsonify({"error": "User not found"}), 404

# @app.route("/api/users/verify", methods=["POST"])
# def verify_password():
#     """API to verify user credentials"""
#     data = request.json
#     if not data:
#         return jsonify({"error": "Invalid request"}), 400

#     email = data.get("email")
#     password = data.get("password")

#     if user_model.verify_password(email, password):
#         return jsonify({"message": "Password verified"}), 200
#     return jsonify({"error": "Invalid email or password"}), 401

# def get_all_admin(): 
#     '''Returns all admin users'''
#     return list(user_model.collection.find({"isAdmin": True}).sort("_id", 1))

# # Run the app
# if __name__ == "_main_":
#     app.run(debug=True)


from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify

class UserModel:
    def __init__(self, db):
        self.collection = db.users  # Assuming the collection is named 'users'

    def create_user(self, email, password, role, name):
        """Creates a new user"""
        hashed_password = generate_password_hash(password)
        user_data = {
            "Email": email,
            "Password": hashed_password,
            "Role": role,
            "Name": name
        }
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

#     def find_user_by_email(self, email):
#         """Finds a user by email"""
#         return self.collection.find_one({"Email": email})

    def verify_password(self, email, password):
        """Verifies the password for a given email"""
        user = self.find_user_by_email(email)
        if user and check_password_hash(user["Password"], password):
            return str(user["_id"])  # Return user_id (MongoDB _id) after verifying password
        return None  # Return None if password doesn't match

    def update_user(self, email, updates):
        """Updates user data"""
        result = self.collection.update_one({"Email": email}, {"$set": updates})
        return result.modified_count > 0

#     def delete_user(self, email):
#         """Deletes a user by email"""
#         result = self.collection.delete_one({"Email": email})
#         return result.deleted_count > 0

    def get_all_users(self):
        """Returns all users"""
        return list(self.collection.find({}, {"_id": 0}))  # Excluding MongoDB _id

# # Run the app
# if __name__ == "main":
#     app.run(debug=True)