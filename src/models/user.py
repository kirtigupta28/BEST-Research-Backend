from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify
from app import app, db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, current_user
from bson import ObjectId

#id, institution_id, email, password, role, name
class UserModel:
    def __init__(self, db):
        self.collection = db.users  # Assuming the collection is named 'users'

    def create_user(self, data):
        """Creates a new user"""
        from ..models import get_institute_by_name
        hashed_password = generate_password_hash(data.get("password"))
        institution_id = get_institute_by_name(data.get("institution"))
        user_data = {
            "name": data["name"], 
            "password": hashed_password, 
            "institution_id": institution_id, 
            "role": "Faculty", 
            "email": data["email"]
        }
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def retrieve_user(self, filter): 
        try: 
            result = self.collection.find_one(filter)
            print(result) 
            return result 
        except Exception as e: 
            return None 
    
    def find_user_by_email(self, email):
        """Finds a user by email"""
        return self.collection.find_one({"email": email})

    def verify_password(self, email, password):
        """Verifies the password for a given email"""
        user = self.find_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            return user  # Return user_id (MongoDB _id) after verifying password
        return None  # Return None if password doesn't match

    def update_user(self, email, updates):
        """Updates user data"""
        result = self.collection.update_one({"Email": email}, {"$set": updates})
        return result.modified_count > 0

    def delete_user(self, email):
        """Deletes a user by email"""
        result = self.collection.delete_one({"Email": email})
        return result.deleted_count > 0

    def get_all_users(self):
        """Returns all users"""
        return list(self.collection.find({}, {"_id": 0}))  # Excluding MongoDB _id

user_model = UserModel(db)
jwt = JWTManager(app)

@app.route("/api/users/register", methods=["POST"])
def register_user():
    """API to register a new user"""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    user = user_model.find_user_by_email(data.get("email"))
    if (user): 
        return jsonify({"message": "User already exists"}), 409

    user_id = user_model.create_user(data)
    return jsonify({"message": "User created", "user_id": user_id}), 201

@app.route("/api/users/login", methods=["POST"])
def login():
    """API to log in a user and generate a JWT token"""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = data.get("email")
    password = data.get("password")

    user = user_model.verify_password(email, password)
    if user:
        # Generate JWT token
        additional_claims = {"role": user.get("role")}
        access_token = create_access_token(identity=str(user.get("_id")), additional_claims=additional_claims)
        return jsonify({"message": "Login successful", "accessToken": access_token}), 200
    return jsonify({"error": "Invalid email or password"}), 401

@app.route("/api/users/me", methods=["GET"])
@jwt_required()
def protected():
    # We can now access our sqlalchemy User object via `current_user`.
    print(current_user)
    return jsonify(
        id=str(current_user.get("_id")),
        name=current_user.get("name"),
        email=current_user.get("email"),
        role=current_user.get("role")
    )


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    print(identity)
    return user_model.retrieve_user({"_id": ObjectId(identity)})



# #######################


@app.route("/api/users", methods=["GET"])
def get_users():
    """API to fetch all users"""
    users = user.get_all_users()
    return jsonify(users), 200



@app.route("/api/users/<email>", methods=["DELETE"])
def delete_user(email):
    """API to delete a user by email"""
    if user.delete_user(email):
        return jsonify({"message": f"User with email {email} deleted"}), 200
    return jsonify({"error": "User not found"}), 404


# def get_all_admin(): 
#     '''Returns all admin users'''
#     # admins = user_model.collection.find({"isAdmin": True}).sort("_id", 1)
#     # dic = [{"_id": str(admin.get("_id")), **admin} for admin in admins]
#     # print (dic)
#     # return [{"_id": str(admin.get("_id")), **admin} for admin in admins]

#     return list(user_model.collection.find({"isAdmin": True}).sort("_id", 1))

def get_all_admin():
    '''Returns all admin users'''
    admins = user.collection.find({"isAdmin": True}).sort("_id", 1)
    
    # Convert ObjectId to string for each admin document
    return [{"_id": str(admin["_id"]), "isAdmin": admin.get("isAdmin")} for admin in admins]
    