from .user import UserRoutes

def register_routes(app):
    """Register all routes to the Flask app."""
    UserRoutes().get_router()
