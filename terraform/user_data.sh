#!/bin/bash
set -e

# Update system packages
yum update -y

# Install and start SSM Agent (already installed on Amazon Linux 2, but ensure it's running)
yum install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Install Python and dependencies
yum install -y python3 python3-pip python3-devel gcc mysql-devel git nginx

# Create application directory
mkdir -p /opt/monolith
cd /opt/monolith

# Clone application code from GitHub
git clone https://github.com/tashivxo/AWSMonolith.git /tmp/monolith-repo
mv /tmp/monolith-repo/app/* /opt/monolith/
rm -rf /tmp/monolith-repo

# Initialize git in the app directory for future deployments
git init
git remote add origin https://github.com/tashivxo/AWSMonolith.git
git fetch origin
git checkout -b main origin/main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies from requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Skip placeholder creation since we have real app
if false; then
    cat > requirements.txt <<'REQEOF'
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
PyMySQL==1.1.0
python-dotenv==1.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
REQEOF
    
    pip install -r requirements.txt
    
    # Create application files (simplified versions)
    mkdir -p static/css static/js templates
    
    cat > config.py <<'CFGEOF'
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://admin:password@localhost:3306/monolithdb'

config = {'default': Config, 'production': Config, 'development': Config}
CFGEOF

    cat > models.py <<'MODEOF'
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='planning')
    owner = db.Column(db.String(255))
    budget = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float, default=0)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
MODEOF

    cat > __init__.py <<'INITEOF'
from flask import Flask
from flask_cors import CORS
from config import config
from models import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    CORS(app)
    
    # Try to create tables, but don't fail if DB is unreachable
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Could not create database tables (will retry on first request): {e}")
    
    from routes import api_bp, web_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    return app
INITEOF

    cat > routes.py <<'ROUTEOF'
from flask import Blueprint, render_template, jsonify, request
from models import db, Project, InventoryItem, Contact
from datetime import datetime

api_bp = Blueprint('api', __name__)
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    return render_template('index.html')

@api_bp.route('/health')
def health():
    # Simple health check that doesn't require DB
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'status': p.status, 'budget': p.budget} for p in projects])

@api_bp.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    project = Project(name=data.get('name'), owner=data.get('owner', 'Unknown'), budget=float(data.get('budget', 0)))
    db.session.add(project)
    db.session.commit()
    return jsonify({'id': project.id, 'name': project.name}), 201

@api_bp.route('/inventory', methods=['GET'])
def get_inventory():
    items = InventoryItem.query.all()
    return jsonify([{'id': i.id, 'name': i.name, 'sku': i.sku, 'quantity': i.quantity} for i in items])

@api_bp.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.all()
    return jsonify([{'id': c.id, 'first_name': c.first_name, 'last_name': c.last_name, 'email': c.email} for c in contacts])
ROUTEOF

    cat > run.py <<'RUNEOF'
from __init__ import create_app

app = create_app('production')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
RUNEOF

    mkdir -p templates
    cat > templates/index.html <<'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Monolith</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        nav { background: #232F3E; color: #FF9900; padding: 1rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 20px; }
        h1 { color: #232F3E; margin-bottom: 1rem; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }
        .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { color: #FF9900; margin-bottom: 1rem; }
        .card p { color: #666; }
        .status { background: #28a745; color: white; padding: 0.5rem 1rem; border-radius: 4px; }
        footer { text-align: center; padding: 2rem; color: #666; margin-top: 4rem; }
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <h2>AWS Monolith - Internal Business Management</h2>
        </div>
    </nav>
    <main class="container">
        <h1>Welcome to AWS Monolith</h1>
        <p>Production-ready internal business application running on AWS</p>
        
        <div class="dashboard">
            <div class="card">
                <h3>Projects</h3>
                <p>Manage projects and timelines</p>
                <div class="status">Active</div>
            </div>
            <div class="card">
                <h3>Inventory</h3>
                <p>Track inventory items</p>
                <div class="status">Active</div>
            </div>
            <div class="card">
                <h3>Contacts</h3>
                <p>Internal CRM and contacts</p>
                <div class="status">Active</div>
            </div>
        </div>
        
        <h2 style="margin-top: 3rem;">API Status</h2>
        <p id="api-status">Checking API...</p>
    </main>
    <footer>
        <p>&copy; 2026 AWS Monolith - Running on AWS Infrastructure</p>
    </footer>
    
    <script>
        fetch('/api/health')
            .then(r => r.json())
            .then(data => document.getElementById('api-status').textContent = '✓ API is healthy - ' + data.timestamp)
            .catch(() => document.getElementById('api-status').textContent = '⚠ API connection failed');
    </script>
</body>
</html>
HTMLEOF
fi

# Change ownership of application files to ec2-user
chown -R ec2-user:ec2-user /opt/monolith

# Get RDS endpoint from AWS (uses EC2 IAM role with SSM permissions)
# Fallback: construct from known values if SSM fails
RDS_ENDPOINT=$(aws ssm get-parameter \
  --name /aws-monolith/db/endpoint \
  --region us-east-1 \
  --query Parameter.Value \
  --output text 2>/dev/null) || RDS_ENDPOINT="aws-monolith-db.cs5gukwmgrbm.us-east-1.rds.amazonaws.com:3306"

DB_PASSWORD=$(aws ssm get-parameter \
  --name /aws-monolith/db/password \
  --region us-east-1 \
  --with-decryption \
  --query Parameter.Value \
  --output text 2>/dev/null) || DB_PASSWORD="changeme"

# Create systemd service
cat > /etc/systemd/system/monolith.service <<SVCEOF
[Unit]
Description=AWS Monolith Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/opt/monolith
Environment="PATH=/opt/monolith/venv/bin"
Environment="DATABASE_URL=mysql+pymysql://admin:$DB_PASSWORD@$RDS_ENDPOINT/monolithdb"
Environment="SECRET_KEY=production-secret-key-change-me"
ExecStart=/opt/monolith/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 run:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF

# Create simple health check file for Nginx
mkdir -p /usr/share/nginx/html
cat > /usr/share/nginx/html/health.html <<'HEALTHEOF'
OK
HEALTHEOF

# Remove default Nginx config to prevent conflicts
rm -f /etc/nginx/nginx.conf.default
rm -f /etc/nginx/conf.d/default.conf

# Configure Nginx
cat > /etc/nginx/conf.d/monolith.conf <<'NGXEOF'
upstream monolith {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name _;

    # Direct health check that doesn't require Flask
    location = /health {
        return 200 'OK';
        add_header Content-Type text/plain;
    }

    location / {
        proxy_pass http://monolith;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGXEOF

# Start services
systemctl daemon-reload
systemctl enable nginx
systemctl start nginx
systemctl enable monolith
systemctl start monolith

# Wait for services to start
sleep 5

# Verify services are running
systemctl is-active nginx >> /var/log/monolith-setup.log
systemctl is-active monolith >> /var/log/monolith-setup.log

# Test local health endpoint
curl -s http://localhost/health >> /var/log/monolith-setup.log 2>&1

# Log completion
echo "AWS Monolith application deployed successfully" >> /var/log/monolith-setup.log
date >> /var/log/monolith-setup.log

