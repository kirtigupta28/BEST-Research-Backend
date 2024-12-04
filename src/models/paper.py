from app import app, db 
from flask import request, jsonify, send_file, make_response
from bson import ObjectId
from ..utils import upload_pdf, get_pdf, delete_pdf, keygen, encrypt_file, encrypt, point_to_hex
from gridfs import GridFS
import io
from .common_public_key import get_common_public_key

grid_fs = GridFS(db)
class PaperModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.papers  # Assuming the collection is named 'papers'
    
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
            
            # Key for pdf encryption
            symm_keygen = keygen()

            # Encrypt the file
            encrypt_pdf_file = encrypt_file(pdf_file, symm_keygen)

            # Encrypt the key
            common_public_key = get_common_public_key()

            print(symm_keygen)
            print(common_public_key)
            
            # C2 is the encrypted symmetric key (error here)
            C1, C2 = encrypt(symm_keygen, common_public_key)
        
            # Save the file to GridFS
            file_id = upload_pdf(encrypt_pdf_file, grid_fs)
            print(C1)
            print(C2)

            # Extract other fields from the request
            subject_code = request.form.get('subject_code')
            year = request.form.get('year')
            branch = request.form.get('branch')
            exam = request.form.get('exam')
            faculty = request.form.get('faculty')

            if not all([subject_code, year, branch, exam, faculty]):
                return jsonify({"error": "All fields are required"}), 400

            paper_data = {
                "pdf_id": ObjectId(file_id),
                "subject_code": subject_code,
                "year": year,
                "branch": branch,
                "exam": exam,
                "faculty": ObjectId(faculty), 
                "C1": point_to_hex(C1), 
                "encrypted_key": C2
            }
            result = self.collection.insert_one(paper_data)
            return jsonify({
                "message": "Paper uploaded successfully",
                "id": str(result.inserted_id)  # Convert ObjectId to string
            }), 201
        
        except Exception as e:
            print("hello", str(e))
            return jsonify({"error": str(e)}), 400

    def find_pdf_by_id(self, id):
        """
        Find a paper by id.
        :param subject_code: id to search for
        :return: Document with paper details or None
        """
        # exam_data = self.collection.find_one({"_id": id})
        # return exam_data

        try:
            response = get_pdf(id, grid_fs)
            return response
            
        except Exception as e:
            return jsonify({"error": str(e)}), 404
        
    def find_paper_by_id(self, id):
        """
        Find a paper by id.
        :param subject_code: id to search for
        :return: Document with paper details or None
        """
        paper_data = self.collection.find_one({"_id": id})
        pdf_id = paper_data["pdf_id"]
        
        # Retrieve the PDF file from GridFS
        response = get_pdf(ObjectId(pdf_id), grid_fs)
        # print(response)

        # Add the PDF data to the paper data
        # paper_data["pdf"] = response_pdf.data

        for key, value in paper_data.items():
            response.headers[key] = str(value)

        # print(response.headers)
        return response
    
    def delete_paper(self, id):
        """
        Delete a paper by subject code.
        :param subject_code: Subject code of the paper to delete
        :return: True if deletion succeeded, False otherwise
        """
        try: 
            paper_data = self.collection.find_one({"_id": id})
            pdf_id = paper_data["pdf_id"]
            # Delete the PDF file from GridFS
            response_pdf = delete_pdf(ObjectId(pdf_id), grid_fs)
            result = self.collection.delete_one({"_id": id})
            return result.deleted_count > 0
        except Exception as e:
            return False


# Initialize the PaperModel
paper_model = PaperModel(db)



@app.route("/api/paper", methods=["POST"])
def create_paper():
    """
    API endpoint to create a new paper entry.
    Expects JSON body with keys: PDF_Link, Subject_Code, Year, Branch, Exam, Associated_Faculty
    """
    print("Creating paper...")
    return paper_model.create_paper()

@app.route("/api/paper/pdf/<string:id>", methods=["GET"])
def get_pdf_by_id(id):
    """
    API endpoint to retrieve paper details by subject code.
    """
    try:
        paper_data = paper_model.find_pdf_by_id(ObjectId(id))
        return paper_data
    except Exception as e:
        return jsonify({"error": "Paper not found"}), 404
    
@app.route("/api/paper/<string:id>", methods=["GET"])
def get_paper_by_id(id):
    """
    API endpoint to retrieve paper details by id.
    """
    try:
        paper_data = paper_model.find_paper_by_id(ObjectId(id))
        return paper_data
    except Exception as e:
        return jsonify({"error": "Paper not found"}), 404
    

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