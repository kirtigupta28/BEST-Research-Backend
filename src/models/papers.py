from app import app, db
from flask import request, jsonify
from bson import ObjectId
from .subject import SubjectModel
from .institution import Institution
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, current_user

class PapersModel: 
    def __init__(self, db):
        self.__collection__ = db.papers

    #add string of paper
    def add_paper(self, data, user_id): 
        "id, user_id, subject_id, exam_type, C1, C2, sign"
        try:
            subject_data = SubjectModel(db).get_subject_data_by_code(data["subject"])
            print(subject_data)
            if not subject_data or not subject_data.get('_id'):
                return None 
            paper_data={
                "user_id": user_id, 
                "subject_id": subject_data.get("_id"), 
                "exam_type": data["exam_type"], 
                "C1": data.get("C1", ""), 
                "C2": data.get("C2", ""),
                "sign": data["sign"], 
                "ciphertext": data["ciphertext"]
            }
            response = self.__collection__.insert_one(paper_data)
            if response: 
                return response 
            return None 
        except Exception as e: 
            return None 
        
    # def get_all_papers_for_institute(self, name):
    #     try: 
    #         institute = Institution.get_institution_by_name(name)
    #         print(institute)
    #         if not institute: 
    #             return None 
    #         # check if user is part of institute
    #         print(institute_id)
    #         res = self.__collection__find({})
    #         # iterate through all papers and check if user is part of institute
    #         res = list[res]
    #         data = []
    #         for paper in res: 
    #             user = paper.get("user_id")
    #             if user: 
    #                 user = db.users.find_one({"_id": ObjectId(user)}, {"_id": 0})
    #                 if user and user.get("institution_id") == institute_id: 
    #                     data.append(paper)
    #         return data
    #     except Exception as e: 
    #         return None

    def get_all_papers(self): 
        try: 
            res = self.__collection__.find({})
            if not res:
                return None
            papers = list(res)
            data = []
            for paper in papers: 
                #get user data
                user = db.users.find_one({"_id": ObjectId(paper["user_id"])}, {"_id": 0, "institution_id": 0})
                if user: 
                    paper["user"] = user
                #get subject data
                subject = db.subject.find_one({"_id": ObjectId(paper["subject_id"])}, {"_id": 0})
                if subject: 
                    paper["subject"] = subject
                
                new_data = {
                    "user": paper["user"], 
                    "subject": paper["subject"], 
                    "exam_type": paper["exam_type"], 
                    "paper_id": str(paper["_id"]),
                }

                data.append(new_data)            
            return data
        except Exception as e: 
            return None

paper_model = PapersModel(db)

@app.route("/api/papers", methods=["GET"])
def get_all_list_of_papers(): 
    try: 
        res = paper_model.get_all_papers()
        if not res: 
            return jsonify({"message": "No papers found"}), 404
        return jsonify(res), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 40
    

@app.route("/api/papers/", methods=["POST"])
@jwt_required()
def upload_paper(): 
    data = request.json
    user_id = current_user.get("_id")
    response = paper_model.add_paper(data, user_id)
    if response: 
        return jsonify({"message": "Paper uploaded successfully!"}), 201
    
    return jsonify({"message": "Error in uploading paper"}), 400 




# @app.route("/api/papers", methods=["GET"])
# def get_papers(): 
#     try: 
#         name = request.args.get('institute') 
#         #send institute name as query param
#         res = paper_model.get_all_papers_for_institute(name)
#         if res: 
#             return jsonify(res), 200
#         else: 
#             return jsonify({"message": "No papers found"}), 404
#     except Exception as e: 
#         return jsonify({"error": str(e)}), 400
    

#Assumption: User making paper is making for it's own orgnaization
# @app.route("/api/papers", methods=["GET"])
# def get_paper_by_institution(): 
#     name = request.args.get('name') 
#     #retrieve institue by id 
#     institute_id = Institution.get_institution_by_name(name)
#     data = request.json

