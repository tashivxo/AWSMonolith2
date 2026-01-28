#!/usr/bin/env python
import os
import sys

# Ensure the current directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app

# Create Flask app instance for Gunicorn
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # This block is for local development only
    with app.app_context():
        from models import db
        db.create_all()
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
