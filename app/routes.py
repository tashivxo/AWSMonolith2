from flask import Blueprint, render_template, request, jsonify
from models import db, Project, InventoryItem, Contact
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create blueprints
api_bp = Blueprint('api', __name__)
web_bp = Blueprint('web', __name__)

# ============================================
# Web Routes (Frontend)
# ============================================

@web_bp.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@web_bp.route('/projects')
def projects_page():
    """Projects page"""
    return render_template('index.html')

@web_bp.route('/inventory')
def inventory_page():
    """Inventory page"""
    return render_template('index.html')

@web_bp.route('/contacts')
def contacts_page():
    """Contacts page"""
    return render_template('index.html')

# ============================================
# API Routes - Health Check
# ============================================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'AWS Monolith API is running'
    }), 200

# ============================================
# API Routes - Projects
# ============================================

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = Project.query.all()
        return jsonify([p.to_dict() for p in projects]), 200
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        return jsonify({'error': 'Failed to fetch projects'}), 500

@api_bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name') or not data.get('owner') or not data.get('status'):
            return jsonify({'error': 'Missing required fields: name, owner, status'}), 400
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            status=data['status'],
            owner=data['owner'],
            budget=data.get('budget', 0.0),
            start_date=datetime.fromisoformat(data.get('start_date', datetime.now().isoformat())),
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify(project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating project: {str(e)}")
        return jsonify({'error': 'Failed to create project'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch project'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'status' in data:
            project.status = data['status']
        if 'owner' in data:
            project.owner = data['owner']
        if 'budget' in data:
            project.budget = data['budget']
        if 'start_date' in data:
            project.start_date = datetime.fromisoformat(data['start_date'])
        if 'end_date' in data:
            project.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(project.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating project {project_id}: {str(e)}")
        return jsonify({'error': 'Failed to update project'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete project'}), 500

# ============================================
# API Routes - Inventory Items
# ============================================

@api_bp.route('/inventory', methods=['GET'])
def get_inventory():
    """Get all inventory items"""
    try:
        items = InventoryItem.query.all()
        return jsonify([i.to_dict() for i in items]), 200
    except Exception as e:
        logger.error(f"Error fetching inventory: {str(e)}")
        return jsonify({'error': 'Failed to fetch inventory'}), 500

@api_bp.route('/inventory', methods=['POST'])
def create_inventory_item():
    """Create a new inventory item"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'sku', 'quantity', 'unit_price', 'category', 'reorder_level']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        item = InventoryItem(
            name=data['name'],
            sku=data['sku'],
            description=data.get('description', ''),
            quantity=data['quantity'],
            unit_price=data['unit_price'],
            category=data['category'],
            location=data.get('location', ''),
            reorder_level=data['reorder_level']
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify(item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating inventory item: {str(e)}")
        return jsonify({'error': 'Failed to create inventory item'}), 500

@api_bp.route('/inventory/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    """Get a specific inventory item"""
    try:
        item = InventoryItem.query.get(item_id)
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        return jsonify(item.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching inventory item {item_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch inventory item'}), 500

@api_bp.route('/inventory/<int:item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    """Update an inventory item"""
    try:
        item = InventoryItem.query.get(item_id)
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            item.name = data['name']
        if 'sku' in data:
            item.sku = data['sku']
        if 'description' in data:
            item.description = data['description']
        if 'quantity' in data:
            item.quantity = data['quantity']
        if 'unit_price' in data:
            item.unit_price = data['unit_price']
        if 'category' in data:
            item.category = data['category']
        if 'location' in data:
            item.location = data['location']
        if 'reorder_level' in data:
            item.reorder_level = data['reorder_level']
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating inventory item {item_id}: {str(e)}")
        return jsonify({'error': 'Failed to update inventory item'}), 500

@api_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    try:
        item = InventoryItem.query.get(item_id)
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Inventory item deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting inventory item {item_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete inventory item'}), 500

# ============================================
# API Routes - Contacts
# ============================================

@api_bp.route('/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts"""
    try:
        contacts = Contact.query.all()
        return jsonify([c.to_dict() for c in contacts]), 200
    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        return jsonify({'error': 'Failed to fetch contacts'}), 500

@api_bp.route('/contacts', methods=['POST'])
def create_contact():
    """Create a new contact"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['first_name', 'last_name', 'email']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        contact = Contact(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone', ''),
            department=data.get('department', ''),
            job_title=data.get('job_title', ''),
            company=data.get('company', ''),
            notes=data.get('notes', ''),
            status=data.get('status', 'active')
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify(contact.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating contact: {str(e)}")
        return jsonify({'error': 'Failed to create contact'}), 500

@api_bp.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a specific contact"""
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        return jsonify(contact.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching contact {contact_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch contact'}), 500

@api_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update a contact"""
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        data = request.get_json()
        
        if 'first_name' in data:
            contact.first_name = data['first_name']
        if 'last_name' in data:
            contact.last_name = data['last_name']
        if 'email' in data:
            contact.email = data['email']
        if 'phone' in data:
            contact.phone = data['phone']
        if 'department' in data:
            contact.department = data['department']
        if 'job_title' in data:
            contact.job_title = data['job_title']
        if 'company' in data:
            contact.company = data['company']
        if 'notes' in data:
            contact.notes = data['notes']
        if 'status' in data:
            contact.status = data['status']
        
        contact.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(contact.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating contact {contact_id}: {str(e)}")
        return jsonify({'error': 'Failed to update contact'}), 500

@api_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        db.session.delete(contact)
        db.session.commit()
        
        return jsonify({'message': 'Contact deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting contact {contact_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete contact'}), 500
