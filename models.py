from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class POHeader(db.Model):
    __tablename__ = 'po_header'
    
    po_id = db.Column(db.String(10), primary_key=True)  # 10 digit number starts with 2
    status = db.Column(db.String(20), nullable=False)  # inprogress, received, hold
    last_updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with PO Line
    po_lines = db.relationship('POLine', backref='po_header_ref', lazy=True)
    
    def __repr__(self):
        return f'<POHeader {self.po_id}>'

class POLine(db.Model):
    __tablename__ = 'po_line'
    
    id = db.Column(db.Integer, primary_key=True)
    pallet_id = db.Column(db.String(15), nullable=False)  # 15 digit number starts with 5
    po_id = db.Column(db.String(10), db.ForeignKey('po_header.po_id'), nullable=False)
    asn_id = db.Column(db.String(5), nullable=False)  # 5 digit number starts with 0
    last_updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<POLine {self.pallet_id}>'

class ASNHeader(db.Model):
    __tablename__ = 'asn_header'
    
    asn_id = db.Column(db.String(5), primary_key=True)  # 5 digit number starts with 0
    last_updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    supplier_reference = db.Column(db.String(50), nullable=False)  # e.g., abc123
    
    # Relationship with ASN Line
    asn_lines = db.relationship('ASNLine', backref='asn_header_ref', lazy=True)
    
    def __repr__(self):
        return f'<ASNHeader {self.asn_id}>'

class ASNLine(db.Model):
    __tablename__ = 'asn_line'
    
    id = db.Column(db.Integer, primary_key=True)
    pallet_id = db.Column(db.String(15), nullable=False)  # 15 digit number starts with 5
    po_id = db.Column(db.String(10), nullable=False)
    asn_id = db.Column(db.String(5), db.ForeignKey('asn_header.asn_id'), nullable=False)
    supplier_reference = db.Column(db.String(50), nullable=False)
    last_updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<ASNLine {self.pallet_id}>'

class IssueTicket(db.Model):
    __tablename__ = 'issue_ticket'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)  # missing_asn, missing_po, missing_pallet, quantity_mismatch
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_date = db.Column(db.DateTime)
    
    # Extracted entities
    asn_id = db.Column(db.String(5))
    po_id = db.Column(db.String(10))
    pallet_id = db.Column(db.String(15))
    
    def __repr__(self):
        return f'<IssueTicket {self.ticket_id}>'