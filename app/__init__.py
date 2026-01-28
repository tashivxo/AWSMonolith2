from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
import sys

# Ensure imports work properly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import config
from models import db

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Setup logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from routes import api_bp, web_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    return app
