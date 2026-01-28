from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    """Project Management Model"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='planning', nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    owner = db.Column(db.String(255), nullable=False)
    budget = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'owner': self.owner,
            'budget': self.budget,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class InventoryItem(db.Model):
    """Inventory Tracking Model"""
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit_price = db.Column(db.Float, default=0.0, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    reorder_level = db.Column(db.Integer, default=10, nullable=False)
    last_restocked = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'category': self.category,
            'location': self.location,
            'reorder_level': self.reorder_level,
            'last_restocked': self.last_restocked.isoformat() if self.last_restocked else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Contact(db.Model):
    """Internal CRM Model"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'job_title': self.job_title,
            'company': self.company,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
