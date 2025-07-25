from flask import Flask, request, jsonify, render_template_string
import logging
import uuid
from datetime import datetime
import threading
import os

from config import Config
from models import db, IssueTicket
from warehouse_processor import WarehouseProcessor
from data_generator import DataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize processor
warehouse_processor = WarehouseProcessor()

# HTML Template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Warehouse Management System - AI Automation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #2c3e50; }
        input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        textarea { height: 100px; resize: vertical; }
        button { background-color: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-right: 10px; }
        button:hover { background-color: #2980b9; }
        .success { color: #27ae60; background-color: #d5f4e6; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .error { color: #e74c3c; background-color: #fadbd8; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .info { color: #2980b9; background-color: #d6eaf8; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .tickets-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .tickets-table th, .tickets-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .tickets-table th { background-color: #3498db; color: white; }
        .tickets-table tr:nth-child(even) { background-color: #f2f2f2; }
        .status-open { color: #e67e22; font-weight: bold; }
        .status-in-progress { color: #f39c12; font-weight: bold; }
        .status-resolved { color: #27ae60; font-weight: bold; }
        .status-closed { color: #95a5a6; font-weight: bold; }
        .sample-issues { background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .sample-issue { background-color: white; padding: 10px; margin: 5px 0; border-left: 4px solid #3498db; cursor: pointer; }
        .sample-issue:hover { background-color: #f8f9fa; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { background-color: #3498db; color: white; padding: 20px; border-radius: 5px; text-align: center; min-width: 150px; }
        .stat-number { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 Warehouse Management System - AI Automation</h1>
        
        <div class="info">
            <strong>System Status:</strong> AI-powered automation system for handling warehouse issues using open-source LLM models.
            <br><strong>Technologies:</strong> Flask, SQLAlchemy, Sentence Transformers, DistilBERT, Faker
        </div>

        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ total_tickets }}</div>
                <div class="stat-label">Total Tickets</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ open_tickets }}</div>
                <div class="stat-label">Open Tickets</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ resolved_tickets }}</div>
                <div class="stat-label">Resolved</div>
            </div>
        </div>

        <h2>📝 Report New Issue</h2>
        <form id="issueForm">
            <div class="form-group">
                <label for="user_email">Your Email:</label>
                <input type="email" id="user_email" name="user_email" required placeholder="user@company.com">
            </div>
            
            <div class="form-group">
                <label for="issue_description">Issue Description:</label>
                <textarea id="issue_description" name="issue_description" required 
                    placeholder="Describe your issue (e.g., ASN 01234 is missing, PO 2123456789 not found, etc.)"></textarea>
            </div>
            
            <button type="submit">🚀 Submit Issue</button>
            <button type="button" onclick="generateSampleData()">🔄 Generate Sample Data</button>
        </form>

        <div class="sample-issues">
            <h3>💡 Sample Issue Descriptions (Click to use):</h3>
            <div class="sample-issue" onclick="fillIssue('ASN 01234 is missing from our system. Please check.')">
                ASN 01234 is missing from our system. Please check.
            </div>
            <div class="sample-issue" onclick="fillIssue('Purchase order 2123456789 is not found in WMS. Please investigate.')">
                Purchase order 2123456789 is not found in WMS. Please investigate.
            </div>
            <div class="sample-issue" onclick="fillIssue('Pallet 512345678901234 is missing for PO 2987654321.')">
                Pallet 512345678901234 is missing for PO 2987654321.
            </div>
            <div class="sample-issue" onclick="fillIssue('Quantity mismatch for pallet 598765432109876 in PO 2456789123.')">
                Quantity mismatch for pallet 598765432109876 in PO 2456789123.
            </div>
        </div>

        <div id="result"></div>

        <h2>🎫 Recent Tickets</h2>
        <table class="tickets-table">
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>User Email</th>
                    <th>Issue Type</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>ASN</th>
                    <th>PO</th>
                    <th>Pallet</th>
                </tr>
            </thead>
            <tbody>
                {% for ticket in tickets %}
                <tr>
                    <td>{{ ticket.ticket_id }}</td>
                    <td>{{ ticket.user_email }}</td>
                    <td>{{ ticket.issue_type.replace('_', ' ').title() }}</td>
                    <td class="status-{{ ticket.status.replace('_', '-') }}">{{ ticket.status.replace('_', ' ').title() }}</td>
                    <td>{{ ticket.created_date.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td>{{ ticket.asn_id or '-' }}</td>
                    <td>{{ ticket.po_id or '-' }}</td>
                    <td>{{ ticket.pallet_id or '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <script>
        function fillIssue(text) {
            document.getElementById('issue_description').value = text;
        }

        function generateSampleData() {
            fetch('/api/generate-sample-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML = 
                    '<div class="success">Sample data generated successfully! Page will refresh in 2 seconds.</div>';
                setTimeout(() => location.reload(), 2000);
            })
            .catch(error => {
                document.getElementById('result').innerHTML = 
                    '<div class="error">Error generating sample data: ' + error + '</div>';
            });
        }

        document.getElementById('issueForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                user_email: formData.get('user_email'),
                issue_description: formData.get('issue_description')
            };
            
            document.getElementById('result').innerHTML = 
                '<div class="info">Processing your issue... This may take a few moments.</div>';
            
            fetch('/api/submit-issue', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('result').innerHTML = 
                        '<div class="success">Issue submitted successfully! Ticket ID: ' + data.ticket_id + 
                        '<br>Issue Type: ' + data.issue_type + 
                        '<br>Extracted Entities: ' + JSON.stringify(data.entities) + '</div>';
                    setTimeout(() => location.reload(), 3000);
                } else {
                    document.getElementById('result').innerHTML = 
                        '<div class="error">Error: ' + data.error + '</div>';
                }
            })
            .catch(error => {
                document.getElementById('result').innerHTML = 
                    '<div class="error">Error submitting issue: ' + error + '</div>';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        tickets = IssueTicket.query.order_by(IssueTicket.created_date.desc()).limit(20).all()
        
        total_tickets = IssueTicket.query.count()
        open_tickets = IssueTicket.query.filter(IssueTicket.status.in_(['open', 'in_progress'])).count()
        resolved_tickets = IssueTicket.query.filter(IssueTicket.status == 'resolved').count()
        
        return render_template_string(HTML_TEMPLATE, 
                                    tickets=tickets,
                                    total_tickets=total_tickets,
                                    open_tickets=open_tickets,
                                    resolved_tickets=resolved_tickets)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return f"Error loading dashboard: {e}", 500

@app.route('/api/submit-issue', methods=['POST'])
def submit_issue():
    """API endpoint to submit new issue"""
    try:
        data = request.get_json()
        
        if not data or not data.get('user_email') or not data.get('issue_description'):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: user_email and issue_description'
            }), 400
        
        # Generate unique ticket ID
        ticket_id = f"WMS-{str(uuid.uuid4())[:8].upper()}"
        
        # Extract entities and classify issue type using AI
        from ai_processor import AIProcessor
        ai_processor = AIProcessor()
        
        entities = ai_processor.extract_entities(data['issue_description'])
        issue_type = ai_processor.classify_issue_type(data['issue_description'])
        
        # Process the issue in a separate thread to avoid blocking
        def process_issue():
            try:
                warehouse_processor.process_issue_ticket(
                    ticket_id=ticket_id,
                    user_email=data['user_email'],
                    issue_description=data['issue_description']
                )
            except Exception as e:
                logger.error(f"Error processing issue {ticket_id}: {e}")
        
        thread = threading.Thread(target=process_issue)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'issue_type': issue_type,
            'entities': entities,
            'message': 'Issue submitted successfully and is being processed'
        })
        
    except Exception as e:
        logger.error(f"Error submitting issue: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-sample-data', methods=['POST'])
def generate_sample_data():
    """API endpoint to generate sample data"""
    try:
        data_generator = DataGenerator()
        
        # Generate sample data
        asn_data, po_data = data_generator.create_sample_data(num_asns=5, num_pos_per_asn=2, num_pallets_per_po=3)
        
        # Create test scenarios
        test_scenarios = data_generator.create_test_scenarios()
        
        return jsonify({
            'success': True,
            'message': 'Sample data generated successfully',
            'asn_count': len(asn_data),
            'po_count': len(po_data),
            'test_scenarios': test_scenarios
        })
        
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """API endpoint to get all tickets"""
    try:
        tickets = IssueTicket.query.order_by(IssueTicket.created_date.desc()).all()
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'ticket_id': ticket.ticket_id,
                'user_email': ticket.user_email,
                'issue_description': ticket.issue_description,
                'issue_type': ticket.issue_type,
                'status': ticket.status,
                'created_date': ticket.created_date.isoformat(),
                'resolved_date': ticket.resolved_date.isoformat() if ticket.resolved_date else None,
                'asn_id': ticket.asn_id,
                'po_id': ticket.po_id,
                'pallet_id': ticket.pallet_id
            })
        
        return jsonify({
            'success': True,
            'tickets': tickets_data
        })
        
    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ticket/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """API endpoint to get specific ticket"""
    try:
        ticket = IssueTicket.query.filter_by(ticket_id=ticket_id).first()
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404
        
        ticket_data = {
            'ticket_id': ticket.ticket_id,
            'user_email': ticket.user_email,
            'issue_description': ticket.issue_description,
            'issue_type': ticket.issue_type,
            'status': ticket.status,
            'created_date': ticket.created_date.isoformat(),
            'resolved_date': ticket.resolved_date.isoformat() if ticket.resolved_date else None,
            'asn_id': ticket.asn_id,
            'po_id': ticket.po_id,
            'pallet_id': ticket.pallet_id
        }
        
        return jsonify({
            'success': True,
            'ticket': ticket_data
        })
        
    except Exception as e:
        logger.error(f"Error getting ticket {ticket_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

if __name__ == '__main__':
    # Create tables
    create_tables()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Warehouse Management System on port {port}")
    logger.info("Access the web interface at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=port, debug=debug)