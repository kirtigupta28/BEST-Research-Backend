from flask import Flask
from flask_pymongo import PyMongo
from dotenv import dotenv_values

secrets = dotenv_values(".env")

def connect_db(): 

    app = Flask(__name__)
    app.config["MONGO_URI"] = secrets["MONGO_URI"]

    # Solve the error in the next line pymongo.errors.InvalidURI

    mongo = PyMongo(app)
    db = mongo.db
    return (app, db)
