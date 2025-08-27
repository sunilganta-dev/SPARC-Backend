from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:buzzBuzz1753@34.28.173.49/SPARC')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_change_in_production')
app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL', 'admin@example.com')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.models import user, religion, background, lifestyle, matchmaker

# Register blueprints
from app.routes.users import users_bp
from app.routes.matches import matches_bp
from app.routes.auth import auth_bp
from app.routes.matchmaker import matchmaker_bp

app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(matches_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(matchmaker_bp, url_prefix='/api/matchmaker')