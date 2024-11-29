from app import app, db 
from flask import request, jsonify
from bson import ObjectId
from ..utils import upload_pdf
from gridfs import GridFS

grid_fs = GridFS(db)
class PaperModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.papers  # Assuming the collection is named 'papers'
    
    def get_all_papers(self):
        """
        Get all papers in the collection.
        :return: List of all documents in the collection
        """
        return list(self.collection.find({}, {"_id": 0}))  # Excludes the MongoDB `_id` field

    def create_paper(self):
        """
        Create a new paper entry.
        :param pdf_link: Link to the uploaded PDF
        :param subject_code: Subject code of the paper
        :param year: Year of the paper
        :param branch: Branch associated with the paper
        :param exam: Exam type (e.g., mid-term, end-term, suppl, re-mid)
        :param associated_faculty: Faculty associated with the paper
        :return: Inserted document ID as a string
        """
        try:
            # Access the file from the request
            if 'pdf_id' not in request.files:
                return jsonify({"error": "No file part in the request"}), 400
        
            pdf_file = request.files['pdf_id']
        
            # Check if a valid file was uploaded
            if pdf_file.filename == '':
                return jsonify({"error": "No selected file"}), 400
        
            # Save the file to GridFS
            file_id = upload_pdf(pdf_file, grid_fs)

            # Extract other fields from the request
            subject_code = request.form.get('subject_code')
            year = request.form.get('year')
            branch = request.form.get('branch')
            exam = request.form.get('exam')
            faculty = request.form.get('faculty')

            if not all([subject_code, year, branch, exam, faculty]):
                return jsonify({"error": "All fields are required"}), 400

            paper_data = {
                "pdf_id": file_id,
                "subject_code": subject_code,
                "year": year,
                "branch": branch,
                "exam": exam,
                "faculty": ObjectId(faculty)
            }
            result = self.collection.insert_one(paper_data)
            return jsonify({
                "message": "Paper uploaded successfully",
                "id": str(result.inserted_id)  # Convert ObjectId to string
            }), 201
        
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def find_paper_by_id(self, id):
        """
        Find a paper by subject code.
        :param subject_code: Subject code to search for
        :return: Document with paper details or None
        """
        return self.collection.find_one({"_id": id})

    def update_paper(self, subject_code, updates):
        """
        Update paper details for a specific subject code.
        :param subject_code: Subject code to identify the paper
        :param updates: Dictionary of fields to update
        :return: True if update succeeded, False otherwise
        """
        result = self.collection.update_one({"Subject_Code": subject_code}, {"$set": updates})
        return result.modified_count > 0

    def delete_paper(self, subject_code):
        """
        Delete a paper by subject code.
        :param subject_code: Subject code of the paper to delete
        :return: True if deletion succeeded, False otherwise
        """
        result = self.collection.delete_one({"Subject_Code": subject_code})
        return result.deleted_count > 0



# Initialize the PaperModel
paper_model = PaperModel(db)

@app.route("/api/paper", methods=["GET"])
def get_all_papers():
    """
    API endpoint to retrieve all papers.
    """
    all_papers = paper_model.get_all_papers()
    return jsonify(all_papers), 200


@app.route("/api/paper", methods=["POST"])
def create_paper():
    """
    API endpoint to create a new paper entry.
    Expects JSON body with keys: PDF_Link, Subject_Code, Year, Branch, Exam, Associated_Faculty
    """
    return paper_model.create_paper()

@app.route("/api/paper/<string:id>", methods=["GET"])
def get_paper_by_id(id):
    """
    API endpoint to retrieve paper details by subject code.
    """
    paper_data = paper_model.find_paper_by_id(ObjectId(id))
    if paper_data:
        return jsonify(paper_data), 200
    return jsonify({"error": "Paper not found"}), 404


@app.route("/api/paper/<string:id>", methods=["PUT"])
def update_paper(id):
    """
    API endpoint to update paper details for a specific subject code.
    Expects JSON body with the fields to update.
    """
    updates = request.json
    success = paper_model.update_paper(ObjectId(id), updates)
    if success:
        return jsonify({"message": "Paper updated successfully"}), 200
    return jsonify({"error": "Failed to update paper"}), 400


@app.route("/api/paper/<string:id>", methods=["DELETE"])
def delete_paper(id):
    """
    API endpoint to delete a paper by subject code.
    """
    success = paper_model.delete_paper(ObjectId(id))
    if success:
        return jsonify({"message": "Paper deleted successfully"}), 200
    return jsonify({"error": "Paper not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)