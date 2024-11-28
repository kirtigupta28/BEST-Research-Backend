from src.utils import connect_db

app, db = connect_db()

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