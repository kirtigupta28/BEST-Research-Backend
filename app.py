from src.utils import connect_db
from flask_cors import CORS, cross_origin

app, db = connect_db()

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

import src.routes
import src.firebase