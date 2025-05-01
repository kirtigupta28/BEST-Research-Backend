from app import app, db
from flask import request, jsonify
from bson import ObjectId
from .subject import SubjectModel
from .institution import Institution

class PapersModel: 
    def __init__(self, db):
        self.__collection__ = db.papers

    #add string of paper
    def add_paper(self, data): 
        "id, user_id, subject_id, exam_type, C1, C2, sign"
        try:
            subject_data = SubjectModel(db).get_subject_data_by_code(data["subject"])
            if not subject_data or not subject_data.get('_id'):
                return None 
            paper_data={
                "user_id": ObjectId(data["user_id"]), 
                "subject_id": subject_data.get("_id"), 
                "exam_type": data["exam_type"], 
                "C1": data["C1"], 
                "C2": data["C2"], 
                "sign": data["sign"]
            }
            response = self.__collection__.insert_one(paper_data)
            if response: 
                return response 
            return None 
        except Exception as e: 
            return None 

paper_model = PapersModel(db)

@app.route("/api/papers/", methods=["POST"])
def upload_paper(): 
    data = request.json
    response = paper_model.add_paper(data)
    if response: 
        return jsonify({"message": "Paper uploaded successfully!"}), 201
    
    return jsonify({"message": "Error in uploading paper"}), 400 

#Assumption: User making paper is making for it's own orgnaization
@app.route("/api/papers", methods=["GET"])
def get_paper_by_institution(): 
    name = request.args.get('name') 
    #retrieve institue by id 
    institute_id = Institution.get_institution_by_name(name)
    data = request.json



