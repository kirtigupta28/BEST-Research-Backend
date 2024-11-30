from src.utils import connect_db

app, db = connect_db()

@app.route("/")
def index():
    return "Welcome to the secure API!"

import src.routes

if __name__ == '__main__':
    app.run(debug=True)
    
