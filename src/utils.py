from flask import Flask, request, jsonify, send_file, make_response
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.utils import secure_filename
from bson import ObjectId
from dotenv import dotenv_values
import io

secrets = dotenv_values(".env")

def connect_db(): 

    app = Flask(__name__)
    app.config["MONGO_URI"] = secrets["MONGO_URI"]

    print("Connecting to MongoDB...")

    mongo = PyMongo(app)
    db = mongo.db
    return (app, db)

def upload_pdf(pdf_file, grid_fs):
    try:
        # Save the file to GridFS
        filename = secure_filename(pdf_file.filename)  # Ensure filename is safe
        file_id = grid_fs.put(pdf_file, filename=filename, content_type='application/pdf')
        
        return str(file_id)

    except Exception as e:
        
        return -1


def get_pdf(file_id, grid_fs):
    try:
        # Retrieve the file from GridFS
        file_data = grid_fs.get(ObjectId(file_id))
        
        # Create a file-like object from the file data
        file_stream = io.BytesIO(file_data.read())
        file_stream.seek(0)
        
        # Return the file as a response
        response = send_file(
            file_stream,
            mimetype=file_data.content_type,
            as_attachment=True,
            download_name=file_data.filename
        )

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 404
    
def delete_pdf(file_id, grid_fs):
    try:
        # Delete the file from GridFS
        grid_fs.delete(ObjectId(file_id))
        
        return jsonify({"message": "File deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 404
