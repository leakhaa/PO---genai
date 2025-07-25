# 🏭 Warehouse Management AI Automation System

An intelligent automation system for handling warehouse management issues using open-source GenAI models. The system automatically processes user reports for missing PO/ASN/Pallet/Quantity mismatch issues and coordinates with SAP systems for resolution.

## 🎯 Overview

This system automates the resolution of four critical warehouse management scenarios:

1. **Missing ASN** - Automated ASN interface verification and triggering
2. **Missing PO** - Purchase Order validation and interface requests
3. **Missing Pallet** - Pallet data reconciliation and updates
4. **Quantity Mismatch** - Automated quantity verification and correction

## 🚀 Technologies Used

### Core Technologies
- **Flask** - Web framework for REST API and web interface
- **SQLAlchemy** - Database ORM for data management
- **SQLite** - Lightweight database for development (easily configurable for PostgreSQL/MySQL)

### AI/ML Components
- **Sentence Transformers** - Text similarity and embeddings (`all-MiniLM-L6-v2`)
- **DistilBERT** - Text classification for sentiment analysis
- **Transformers** - Hugging Face transformers library
- **PyTorch** - Deep learning framework

### Data & Communication
- **Faker** - Synthetic data generation for testing
- **Pandas** - Data manipulation and Excel processing
- **OpenPyXL** - Excel file handling
- **SMTP** - Email communication with users and SAP team

### Development & Testing
- **Python 3.8+** - Core programming language
- **Requests** - HTTP client for testing
- **Threading** - Asynchronous processing

## 📊 Database Schema

### Tables Structure

```sql
-- PO Header: Distinct PO records
PO_HEADER (po_id, status, last_updated_date)

-- PO Line: Pallet details for each PO
PO_LINE (id, pallet_id, po_id, asn_id, quantity, last_updated_date)

-- ASN Header: Distinct ASN records
ASN_HEADER (asn_id, supplier_reference, last_updated_date)

-- ASN Line: Pallet details for each ASN
ASN_LINE (id, pallet_id, po_id, asn_id, supplier_reference, quantity, last_updated_date)

-- Issue Tickets: User-reported issues
ISSUE_TICKET (id, ticket_id, user_email, issue_description, issue_type, status, created_date, resolved_date, asn_id, po_id, pallet_id)
```

### ID Formats
- **ASN ID**: 5 digits starting with 0 (e.g., `01234`)
- **PO ID**: 10 digits starting with 2 (e.g., `2123456789`)
- **Pallet ID**: 15 digits starting with 5 (e.g., `512345678901234`)

## 🔄 System Workflow

### Scenario 1: Missing ASN
1. User reports missing ASN
2. AI extracts ASN ID from description
3. System checks ASN_HEADER and ASN_LINE tables
4. If found: Send success email with data snippets
5. If missing: Email SAP team to trigger ASN interface
6. Wait for SAP response and recheck
7. Send resolution email to user

### Scenario 2: Missing PO
1. User reports missing PO
2. AI extracts PO ID from description
3. System checks PO_HEADER, PO_LINE, and ASN_LINE tables
4. If found: Verify pallet count and quantity consistency
5. If consistent: Send success email
6. If inconsistent: Route to appropriate sub-scenario
7. If missing: Email SAP team to trigger PO interface

### Scenario 3: Missing Pallet
1. User reports missing pallet
2. AI extracts Pallet ID, PO ID, and ASN ID
3. System checks PO_LINE and ASN_LINE for pallet
4. If found: Send success email
5. If missing: Request pallet details from SAP
6. Process Excel response and update database
7. Send resolution email with data comparison

### Scenario 4: Quantity Mismatch
1. User reports quantity discrepancy
2. AI extracts relevant IDs
3. Request detailed data from SAP
4. Compare Excel data with database
5. Identify root cause (missing ASN/PO/Pallet)
6. Apply appropriate resolution scenario
7. Update quantities and send resolution email

## 🤖 AI Processing Features

### Entity Extraction
- **Regex-based patterns** for precise ID extraction
- **Context-aware extraction** using sentence transformers
- **Multi-entity support** in single descriptions

### Issue Classification
- **Keyword-based scoring** for issue type determination
- **Semantic similarity** for ambiguous cases
- **Confidence scoring** for classification accuracy

### Response Generation
- **Template-based email generation**
- **Dynamic content insertion** based on context
- **Multi-stakeholder communication** (users, SAP team)

## 📦 Installation & Setup

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd warehouse-management-ai

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

### Environment Configuration
Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///warehouse_management.db

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SAP_EMAIL=sap_team@company.com

# AI Models
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2

# Application
SECRET_KEY=your-secret-key-here
DEBUG=False
PORT=5000
```

## 🌐 API Endpoints

### Core Endpoints
- `GET /` - Web dashboard interface
- `POST /api/submit-issue` - Submit new issue ticket
- `GET /api/tickets` - List all tickets
- `GET /api/ticket/{ticket_id}` - Get specific ticket
- `POST /api/generate-sample-data` - Generate test data
- `GET /health` - System health check

### API Usage Examples

#### Submit Issue
```bash
curl -X POST http://localhost:5000/api/submit-issue \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "user@company.com",
    "issue_description": "ASN 01234 is missing from our system"
  }'
```

#### Get Tickets
```bash
curl http://localhost:5000/api/tickets
```

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive test suite
python test_system.py

# Test specific URL
python test_system.py http://localhost:5000
```

### Manual Testing via Web Interface
1. Open http://localhost:5000
2. Click "Generate Sample Data"
3. Use sample issue descriptions provided
4. Monitor ticket processing in real-time

### Test Scenarios
The system includes pre-built test scenarios for all four issue types:
- Missing ASN with partial data
- Completely missing PO
- Missing pallet with existing PO/ASN
- Quantity mismatch between PO and ASN

## 📈 Monitoring & Logging

### Logging Configuration
- **INFO level** for normal operations
- **ERROR level** for system failures
- **Structured logging** with timestamps and context
- **File and console output** support

### System Metrics
- Total tickets processed
- Resolution success rate
- Average processing time
- Issue type distribution
- AI classification accuracy

## 🔧 Configuration Options

### AI Model Configuration
```python
# Sentence Transformer Model
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"  # Lightweight, fast
# Alternative: "all-mpnet-base-v2"  # Higher accuracy, slower

# Classification Model
CLASSIFICATION_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
```

### Database Configuration
```python
# SQLite (Development)
DATABASE_URL = "sqlite:///warehouse_management.db"

# PostgreSQL (Production)
DATABASE_URL = "postgresql://user:password@localhost/warehouse_db"

# MySQL (Alternative)
DATABASE_URL = "mysql://user:password@localhost/warehouse_db"
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t warehouse-ai .
docker run -p 5000:5000 warehouse-ai
```

### Environment Variables for Production
```env
DEBUG=False
DATABASE_URL=postgresql://...
EMAIL_USERNAME=production@company.com
EMAIL_PASSWORD=secure_app_password
```

## 📊 Sample Data

The system includes a comprehensive data generator that creates:
- **10 ASNs** with realistic supplier references
- **20 POs** distributed across ASNs
- **60 Pallets** with varying quantities
- **Test scenarios** for each issue type
- **Realistic timestamps** and status values

### Data Relationships
```
ASN (01234) 
├── PO (2123456789) 
│   ├── Pallet (512345678901234) - Qty: 5
│   ├── Pallet (512345678901235) - Qty: 3
│   └── Pallet (512345678901236) - Qty: 2
└── PO (2123456790)
    ├── Pallet (512345678901237) - Qty: 1
    └── Pallet (512345678901238) - Qty: 4
```

## 🔍 Troubleshooting

### Common Issues

#### AI Model Loading Errors
```bash
# Clear cache and reinstall
pip uninstall sentence-transformers transformers
pip install sentence-transformers transformers
```

#### Database Connection Issues
```bash
# Reset database
rm warehouse_management.db
python app.py  # Will recreate tables
```

#### Email Configuration Issues
```bash
# Test SMTP connection
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your_email', 'your_password')
print('SMTP connection successful')
"
```

### Performance Optimization
- **Model caching**: AI models are loaded once at startup
- **Database indexing**: Indexes on frequently queried fields
- **Async processing**: Background threads for ticket processing
- **Connection pooling**: Efficient database connections

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run code formatting
black .

# Run linting
flake8 .

# Run tests
pytest
```

### Code Structure
```
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── models.py             # Database models
├── ai_processor.py       # AI/ML processing
├── warehouse_processor.py # Business logic
├── email_service.py      # Email handling
├── data_generator.py     # Test data generation
├── test_system.py        # Comprehensive testing
└── requirements.txt      # Dependencies
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face** for open-source transformer models
- **Sentence Transformers** for efficient text embeddings
- **Flask** community for excellent web framework
- **Faker** library for realistic test data generation

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@company.com
- Documentation: [Project Wiki]

---

**Built with ❤️ using open-source AI technologies**

 
