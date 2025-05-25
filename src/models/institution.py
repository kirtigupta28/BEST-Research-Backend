from app import app, db
from flask import request, jsonify

class Institution: 
    # id, name
    def __init__(self, db):
        self.collection = db.institution

    def get_all_institutes(self): 
        try: 
            res = self.collection.find({}, {"_id": 0})
            # res = [{**doc, "_id": str(doc["_id"])} for doc in res]
            print(res)
            return list(res)
        except Exception as e: 
            return None 
  

    def get_institution_by_name(self, name): 
        try: 
            res = self.collection.find_one({"name": name})
            return res 
        except Exception as e: 
            return None 
    
    def create_institution(self, data): 
        try: 
            result = self.collection.insert_one(data)
            if result: 
                return str(result.inserted_id)
            return None
        except Exception as e: 
            return None

institute_model = Institution(db)

@app.route("/api/institute", methods=["GET"])
def get_institutes(): 
    try: 
        res = institute_model.get_all_institutes()
        return res 
    except Exception as e: 
        return jsonify({"error": str(e)}), 400


@app.route("/api/institute/", methods=["POST"])
def post_institute():
    try:    
        data = request.json
        inst_id = institute_model.create_institution(data)
        if (inst_id): 
            return jsonify({"message": "Institute created"}), 201
    except Exception as e: 
        raise e

@app.route("/api/institute", methods=["GET"])
def get_institute_by_name(name): 
    try: 
        # name = request.args.get('name') 
        institute = institute_model.get_institution_by_name(name)

        if institute: 
            # return jsonify({"message": "Institute exists", "data": institute}), 200
            return institute.get("_id", "")

        # return jsonify({"message": "Institute doesn't exist"}), 404
        return None 

    except Exception as e: 
        raise e 

    

