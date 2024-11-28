from flask import Flask
from flask_pymongo import PyMongo
from dotenv import dotenv_values

secrets = dotenv_values(".env")

app = Flask(__name__)
app.config["MONGO_URI"] = secrets["MONGO_URI"]

# Solve the error in the next line pymongo.errors.InvalidURI

mongo = PyMongo(app)
db = mongo.db

@app.route('/')
def home():
    db.test.insert_one({'name': 'Flask'})
    # Get first document from the collection
    a = db.test.find_one({'name': 'Flask'})
    print(a)
    # Get all documents from the collection
    b = db.test.find({'name': 'Flask'})
    for item in b:
        print(item)
        # access field
        print(item['name'])
        print(item['_id'])
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)