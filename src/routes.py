from flask import Blueprint
from src.models.paper import paper_model
# from src.models.user_poly_values import user_poly_model
# from src.models.user_shares import user_shares_model
from src.models.user import user_model

# main blueprint to be registered with application
api = Blueprint('api', __name__)

api.register_blueprint(user_model, url_prefix="/users") # http://localhost:5000/api/users
api.register_blueprint(paper_model, url_prefix="/papers") # http://localhost:5000/api/papers