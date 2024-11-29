from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.utils import secure_filename

from dotenv import dotenv_values


secrets = dotenv_values(".env")

def upload_pdf(pdf_file, grid_fs):
    try:
        # Save the file to GridFS
        filename = secure_filename(pdf_file.filename)  # Ensure filename is safe
        file_id = grid_fs.put(pdf_file, filename=filename, content_type='application/pdf')
        
        return str(file_id)

    except Exception as e:
        
        return -1

def connect_db(): 

    app = Flask(__name__)
    app.config["MONGO_URI"] = secrets["MONGO_URI"]

    # Solve the error in the next line pymongo.errors.InvalidURI

    mongo = PyMongo(app)
    db = mongo.db
    return (app, db)
