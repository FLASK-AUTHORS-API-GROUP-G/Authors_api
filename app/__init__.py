
from flask import Flask
from app.extensions import db, migrate, jwt
from flask_bcrypt import Bcrypt

# Initialize Bcrypt outside the create_app function
bcrypt = Bcrypt()

from app.Controllers.auth.auth_controllers import auth
from app.Controllers.authors.author_controller import author

def create_app():
    # Application factory function
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Import models
    from app.Models.author_model import Author
    from app.Models.book_model import Book
    from app.Models.company_model import Company

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(author)

    # Home route
    @app.route("/")
    def home():
        return "Authors API"

    return app

# Only run the app if this script is executed directly
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
