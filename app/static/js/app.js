const API_BASE = '/api';

// Page Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = e.target.dataset.page;
        navigateTo(page);
    });
});

function navigateTo(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    
    // Show selected page
    const pageElement = document.getElementById(`${page}-page`);
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    // Mark nav link as active
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    
    // Load data for page
    if (page === 'projects') loadProjects();
    if (page === 'inventory') loadInventory();
    if (page === 'contacts') loadContacts();
    if (page === 'home') loadDashboard();
}

// ==================== DASHBOARD ====================

async function loadDashboard() {
    try {
        const [projectsRes, inventoryRes, contactsRes] = await Promise.all([
            fetch(`${API_BASE}/projects`),
            fetch(`${API_BASE}/inventory`),
            fetch(`${API_BASE}/contacts`)
        ]);
        
        const projects = await projectsRes.json();
        const inventory = await inventoryRes.json();
        const contacts = await contactsRes.json();
        
        document.getElementById('project-count').textContent = projects.length;
        document.getElementById('inventory-count').textContent = inventory.length;
        document.getElementById('contacts-count').textContent = contacts.length;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ==================== PROJECTS ====================

document.getElementById('project-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const project = {
        name: document.getElementById('project-name').value,
        description: document.getElementById('project-description').value,
        owner: document.getElementById('project-owner').value,
        budget: parseFloat(document.getElementById('project-budget').value) || 0,
        status: document.getElementById('project-status').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(project)
        });
        
        if (response.ok) {
            e.target.reset();
            loadProjects();
            showNotification('Project added successfully!', 'success');
        } else {
            showNotification('Error adding project', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error adding project', 'error');
    }
});

async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects`);
        const projects = await response.json();
        
        const list = document.getElementById('projects-list');
        list.innerHTML = '';
        
        if (projects.length === 0) {
            list.innerHTML = '<div class="empty-message">No projects yet. Create one to get started!</div>';
            return;
        }
        
        projects.forEach(project => {
            const card = document.createElement('div');
            card.className = 'item-card';
            card.innerHTML = `
                <h3>${project.name}</h3>
                <p class="meta"><strong>Owner:</strong> ${project.owner}</p>
                <p class="meta"><strong>Status:</strong> ${project.status}</p>
                <p class="meta"><strong>Budget:</strong> $${project.budget}</p>
                <p>${project.description || 'No description'}</p>
                <div class="actions">
                    <button class="btn btn-small btn-success" onclick="editProject(${project.id})">Edit</button>
                    <button class="btn btn-small btn-danger" onclick="deleteProject(${project.id})">Delete</button>
                </div>
            `;
            list.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function deleteProject(id) {
    if (!confirm('Are you sure?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadProjects();
            showNotification('Project deleted', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error deleting project', 'error');
    }
}

// ==================== INVENTORY ====================

document.getElementById('inventory-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const item = {
        name: document.getElementById('item-name').value,
        sku: document.getElementById('item-sku').value,
        category: document.getElementById('item-category').value,
        description: document.getElementById('item-description').value,
        quantity: parseInt(document.getElementById('item-quantity').value),
        unit_price: parseFloat(document.getElementById('item-price').value) || 0,
        location: document.getElementById('item-location').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/inventory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
        });
        
        if (response.ok) {
            e.target.reset();
            loadInventory();
            showNotification('Item added successfully!', 'success');
        } else {
            showNotification('Error adding item', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error adding item', 'error');
    }
});

async function loadInventory() {
    try {
        const response = await fetch(`${API_BASE}/inventory`);
        const items = await response.json();
        
        const list = document.getElementById('inventory-list');
        list.innerHTML = '';
        
        if (items.length === 0) {
            list.innerHTML = '<div class="empty-message">No inventory items yet. Add one to get started!</div>';
            return;
        }
        
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'item-card';
            card.innerHTML = `
                <h3>${item.name}</h3>
                <p class="meta"><strong>SKU:</strong> ${item.sku}</p>
                <p class="meta"><strong>Category:</strong> ${item.category}</p>
                <p class="meta"><strong>Quantity:</strong> ${item.quantity}</p>
                <p class="meta"><strong>Price:</strong> $${item.unit_price}</p>
                <p class="meta"><strong>Location:</strong> ${item.location || 'N/A'}</p>
                <div class="actions">
                    <button class="btn btn-small btn-success" onclick="editItem(${item.id})">Edit</button>
                    <button class="btn btn-small btn-danger" onclick="deleteItem(${item.id})">Delete</button>
                </div>
            `;
            list.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading inventory:', error);
    }
}

async function deleteItem(id) {
    if (!confirm('Are you sure?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/inventory/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadInventory();
            showNotification('Item deleted', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error deleting item', 'error');
    }
}

// ==================== CONTACTS ====================

document.getElementById('contact-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const contact = {
        first_name: document.getElementById('contact-firstname').value,
        last_name: document.getElementById('contact-lastname').value,
        email: document.getElementById('contact-email').value,
        phone: document.getElementById('contact-phone').value,
        department: document.getElementById('contact-department').value,
        job_title: document.getElementById('contact-title').value,
        company: document.getElementById('contact-company').value,
        notes: document.getElementById('contact-notes').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/contacts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contact)
        });
        
        if (response.ok) {
            e.target.reset();
            loadContacts();
            showNotification('Contact added successfully!', 'success');
        } else {
            showNotification('Error adding contact', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error adding contact', 'error');
    }
});

async function loadContacts() {
    try {
        const response = await fetch(`${API_BASE}/contacts`);
        const contacts = await response.json();
        
        const list = document.getElementById('contacts-list');
        list.innerHTML = '';
        
        if (contacts.length === 0) {
            list.innerHTML = '<div class="empty-message">No contacts yet. Add one to get started!</div>';
            return;
        }
        
        contacts.forEach(contact => {
            const card = document.createElement('div');
            card.className = 'item-card';
            card.innerHTML = `
                <h3>${contact.first_name} ${contact.last_name}</h3>
                <p class="meta"><strong>Email:</strong> ${contact.email}</p>
                <p class="meta"><strong>Phone:</strong> ${contact.phone || 'N/A'}</p>
                <p class="meta"><strong>Department:</strong> ${contact.department || 'N/A'}</p>
                <p class="meta"><strong>Title:</strong> ${contact.job_title || 'N/A'}</p>
                <p class="meta"><strong>Company:</strong> ${contact.company || 'N/A'}</p>
                <p>${contact.notes || 'No notes'}</p>
                <div class="actions">
                    <button class="btn btn-small btn-success" onclick="editContact(${contact.id})">Edit</button>
                    <button class="btn btn-small btn-danger" onclick="deleteContact(${contact.id})">Delete</button>
                </div>
            `;
            list.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading contacts:', error);
    }
}

async function deleteContact(id) {
    if (!confirm('Are you sure?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/contacts/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadContacts();
            showNotification('Contact deleted', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error deleting contact', 'error');
    }
}

// ==================== UTILITIES ====================

function showNotification(message, type = 'info') {
    console.log(`${type.toUpperCase()}: ${message}`);
    // In a real app, you'd show a toast notification
}

// ==================== DARK MODE ====================

const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;
const body = document.body;

// Check for saved theme preference or default to light mode
const currentTheme = localStorage.getItem('theme') || 'light';
if (currentTheme === 'dark') {
    body.classList.add('dark-mode');
    themeToggle.innerHTML = '☀️ Light Mode';
}

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    
    if (body.classList.contains('dark-mode')) {
        themeToggle.innerHTML = '☀️ Light Mode';
        localStorage.setItem('theme', 'dark');
    } else {
        themeToggle.innerHTML = '🌙 Dark Mode';
        localStorage.setItem('theme', 'light');
    }
});

// Load dashboard on page load
window.addEventListener('load', () => {
    loadDashboard();
});
