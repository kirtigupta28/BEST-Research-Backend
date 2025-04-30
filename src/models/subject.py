from app import app, db
from bson.objectid import ObjectId
from pymongo.collection import Collection
from flask import jsonify, request

#subject_id, year, dept, name
class SubjectModel:
    def __init__(self, db):
        self.collection = db.subject  

    def get_subject_data_by_code(self, code): 
        try:
            if not code: 
                return None
            res = self.collection.find_one({"subject_id": code}, {"_id": 0})
            if(res == None):
                return None
            else:
                return res
            # return res
        except Exception as e:
            return None

    def get_subject_data_by_id(self, id): 
        try:
            res = self.collection.find_one({"_id": id}, {"_id": 0})
            if(res == None):
                return {"data": False}
            else:
                return res
            # return res
        except Exception as e:
            return None
    
    def create_subject(self, data): 
        try:        
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        
        except Exception as e: 
            return None 
        
    def get_all_subjects(self): 
        try: 
            res = self.collection.find({}, {"_id": 0})
            print(res)
            return list(res)
        except Exception as e: 
            return None 
        

subject_model = SubjectModel(db)

@app.route("/api/subject", methods=["GET"])
def get_subjects(): 
    try: 
        res = subject_model.get_all_subjects()
        return res 
    except Exception as e: 
        return jsonify({"error": str(e)}), 400

@app.route("/api/subject", methods=["POST"]) 
def post_subject(): 
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    try:
        result = subject_model.get_subject_data_by_code(data.get("subject_id", ""))
        if (result): 
            return jsonify({"message": "Subjct already exists"}), 409

        subject_id = subject_model.create_subject(data)
        return jsonify({"message": "Subject created", "subject_id": subject_id}), 201

    except Exception as e: 
        return jsonify({"error": str(e)}), 400        

@app.route("/api/subject/<string:uid>", methods=["GET"])
def get_subject(uid):
    """
    API endpoint to retrieve user share details by UID.
    """
    try:
        # Retrieve user share by UID
        subject_data = subject_model.get_subject_data_by_id(ObjectId(uid))
        if subject_data:
            return subject_data, 200
    
        return jsonify({"error": "Subject not found"}), 404
   
    except Exception as e:
        return jsonify({"error": str(e)}), 400