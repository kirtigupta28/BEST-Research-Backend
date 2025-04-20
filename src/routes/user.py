from src.models import UserModel
from app import app, db
from flask import request, jsonify

# Initialize UserModel
# user_model = UserModel(db)

class UserRoutes: 
    def __init__(self): 
        self.__connected_model = UserModel(db)
        self.router = app 

    def get_router(self): 
        # Routes
        @self.router.route("/api/users/register", methods=["POST"])
        def register_user():
            """API to register a new user"""
            data = request.json
            if not data:
                return jsonify({"error": "Invalid request"}), 400

            email = data.get("email")
            password = data.get("password")
            role = data.get("role", False)
            name = data.get("name")

            if not all([email, password, name]):
                return jsonify({"error": "Missing required fields"}), 400
            
            user = self.__connected_model.find_user_by_email(email)
            if (user): 
                return jsonify({"message": "User already exists"}), 409

            user_id = self.__connected_model.create_user(email, password, role, name)
            return jsonify({"message": "User created", "user_id": user_id}), 201


        @self.router.route("/api/users", methods=["GET"])
        def get_users():
            """API to fetch all users"""
            users = self.__connected_model.get_all_users()
            return jsonify(users), 200

        @self.router.route("/api/users/<email>", methods=["DELETE"])
        def delete_user(email):
            """API to delete a user by email"""
            if self.__connected_model.delete_user(email):
                return jsonify({"message": f"User with email {email} deleted"}), 200
            return jsonify({"error": "User not found"}), 404

        @self.router.route("/api/users/login", methods=["POST"])
        def verify_password():
            """API to verify user credentials"""
            data = request.json
            if not data:
                return jsonify({"error": "Invalid request"}), 400

            email = data.get("email")
            password = data.get("password")

            user_id = self.__connected_model.verify_password(email, password)
            if user_id:
                return jsonify({"message": "Password verified", "user_id": user_id}), 200
            return jsonify({"error": "Invalid email or password"}), 401

        # def get_all_admin(): 
        #     '''Returns all admin users'''
        #     # admins = user_model.collection.find({"isAdmin": True}).sort("_id", 1)
        #     # dic = [{"_id": str(admin.get("_id")), **admin} for admin in admins]
        #     # print (dic)
        #     # return [{"_id": str(admin.get("_id")), **admin} for admin in admins]

        #     return list(user_model.collection.find({"isAdmin": True}).sort("_id", 1))

        def get_all_admin():
            '''Returns all admin users'''
            admins = self.__connected_model.collection.find({"isAdmin": True}).sort("_id", 1)
            
            # Convert ObjectId to string for each admin document
            return [{"_id": str(admin["_id"]), "isAdmin": admin.get("isAdmin")} for admin in admins]
            
        return self.router