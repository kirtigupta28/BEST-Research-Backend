from src.utils import connect_db
from flask_cors import CORS, cross_origin
from src.routes import register_routes

app, db = connect_db()

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

register_routes()

import src.models
import src.firebase