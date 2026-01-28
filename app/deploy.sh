#!/bin/bash
set -e

echo "Starting AWS Monolith Application Deployment..."

# Variables
APP_DIR="/opt/monolith"
APP_USER="ec2-user"
PYTHON_VERSION="3.11"

# Update system
echo "Updating system packages..."
yum update -y

# Install Python and dependencies
echo "Installing Python and dependencies..."
yum install -y python3 python3-pip python3-devel gcc mysql-devel

# Create application directory
echo "Creating application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or copy application code
echo "Setting up application code..."
if [ -d ".git" ]; then
    git pull origin main
else
    # If not using git, copy files here
    # This section assumes code is deployed via other means
    echo "Application directory ready"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file for production
echo "Creating environment configuration..."
cat > .env <<EOF
FLASK_ENV=production
FLASK_APP=run.py
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:3306/${DB_NAME}
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF

# Initialize database
echo "Initializing database..."
python3 -c "from __init__ import create_app, db; app = create_app('production'); db.create_all()"

# Create systemd service for the application
echo "Creating systemd service..."
cat > /etc/systemd/system/monolith.service <<EOF
[Unit]
Description=AWS Monolith Application
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --access-logfile - --error-logfile - run:app

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "Enabling and starting application service..."
systemctl daemon-reload
systemctl enable monolith
systemctl start monolith

# Install and configure Nginx as reverse proxy
echo "Installing and configuring Nginx..."
yum install -y nginx

cat > /etc/nginx/conf.d/monolith.conf <<EOF
upstream monolith {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 20M;

    location / {
        proxy_pass http://monolith;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable and start Nginx
systemctl enable nginx
systemctl start nginx

# Configure CloudWatch Logs
echo "Configuring CloudWatch Logs..."
yum install -y awslogs

cat > /etc/awslogs/config/monolith.conf <<EOF
[/var/log/monolith.log]
log_group_name = /aws/ec2/monolith
log_stream_name = {instance_id}
datetime_format = %Y-%m-%d %H:%M:%S
file = /var/log/monolith.log
buffer_duration = 5000
initial_tail_file_truncation = false
log_format = %(asctime)s %(levelname)s %(message)s
EOF

systemctl enable awslogsd
systemctl start awslogsd

# Log completion
echo "Deployment completed successfully!" > /var/log/monolith-deployment.log
echo "Application URL: http://$(hostname -I | awk '{print $1}')"

exit 0
