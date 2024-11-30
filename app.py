from src.utils import connect_db

app, db = connect_db()

import src.routes

if __name__ == '__main__':
    app.run(debug=True)