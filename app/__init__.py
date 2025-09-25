from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from config import config

# Global extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(env_name="default"):
    """Application factory function"""
    app = Flask(__name__)

    # Load config
    app.config.from_object(config[env_name])

    # File upload config
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    from app.routes.users import users_bp
    from app.routes.matches import matches_bp
    from app.routes.auth import auth_bp
    from app.routes.matchmaker import matchmaker_bp
    from app.routes.applicants import applicants_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(matches_bp, url_prefix="/api/matches")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(matchmaker_bp, url_prefix="/api/matchmaker")
    app.register_blueprint(applicants_bp, url_prefix="/api/applicants")

    # Serve uploaded pictures
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Health-check route
    @app.route("/")
    def index():
        return {"message": "SPARC Backend is running!"}, 200

    return app
