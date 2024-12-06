from app import app, db 
from flask import request, jsonify, send_file, make_response
from bson import ObjectId
from ..utils import upload_pdf, get_pdf, delete_pdf, keygen, encrypt_file, encrypt, point_to_hex, hex_to_point, decrypt, decrypt_file, convert_pdf_to_bytes
from gridfs import GridFS
import io
from .common_public_key import get_common_public_key
from ecdsa.ecdsa import string_to_int, int_to_string
from ecdsa.curves import SECP256k1, NIST256p
from ecdsa.ellipticcurve import PointJacobi, Point, CurveFp

p = 17  # Prime modulus
a = 2  # Curve coefficient a
b = 2  # Curve coefficient b
order = 19  # Order of the curve
PatInf = [0, 0] #define "Point at Infinity"


# Define the custom curve
curve = CurveFp(p, a, b)

# Define the generator point (on the curve)
G = Point(curve, 5, 1, order)

s1 = "1"
s2 = "6"
s3 = "3"
s4 = "6"

s1_int = int(s1)
s2_int = int(s2)
s3_int = int(s3)
s4_int = int(s4)

sec_key = (s1_int + s2_int + s3_int + s4_int)%(19)


grid_fs = GridFS(db)
class PaperModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.papers  # Assuming the collection is named 'papers'
    
    def create_paper(self):
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
            encrypted_pdf_file = encrypt_file(pdf_file, symm_keygen)
            # Encrypt the key
            Q = get_common_public_key()
            # C2 is the encrypted symmetric key
            C1, C2 = encrypt(Q, string_to_int(symm_keygen))
            # Save the file to GridFS
            file_id = upload_pdf(encrypted_pdf_file, grid_fs)
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
                "encrypted_key": int_to_string(C2)
            }
            result = self.collection.insert_one(paper_data)
            return jsonify({
                "message": "Paper uploaded successfully",
                "id": str(result.inserted_id)  # Convert ObjectId to string
            }), 201
        except Exception as e:
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
            # Retrieve the PDF file from GridFS
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
        C1 = paper_data["C1"]
        C2 = paper_data["encrypted_key"]

        # Decrypt the key 
        point_C1 = hex_to_point(C1) # C1 is point on curve
        encrypted_key = string_to_int(C2) # C2 is int

        # compute sec key

        decrypted_symm_key = decrypt(sec_key, (point_C1, encrypted_key))

        # Retrieve the PDF file from GridFS
        response = get_pdf(ObjectId(pdf_id), grid_fs)

        decrypted_pdf_file = decrypt_file(response.response.file, decrypted_symm_key)

        # convert decrypted pdf file to bytes
        new_response = convert_pdf_to_bytes(decrypted_pdf_file)

        for key, value in paper_data.items():
            new_response.headers[key] = str(value)
        
        return new_response
    
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
        
    # def find_enc_paper_by_id(self, id):
    #     paper_data = self.collection.find_one({"_id": id})
    #     pdf_id = paper_data["pdf_id"]

    #     # Retrieve the PDF file from GridFS
    #     response = get_pdf(ObjectId(pdf_id), grid_fs)

    #     for key, value in paper_data.items():
    #         response.headers[key] = str(value)

    #     print(response)
        
    #     return response



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

# @app.route("/api/paper/enc/<string:id>", methods=["GET"])
# def get_encrypted_paper_by_id(id):
#     """
#     API endpoint to retrieve paper details by id.
#     """
#     try:
#         paper_data = paper_model.find_enc_paper_by_id(ObjectId(id))
#         return jsonify(paper_data)
#     except Exception as e:
#         return jsonify({"error": "Paper not found"}), 404

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