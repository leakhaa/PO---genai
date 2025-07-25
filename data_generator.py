import random
from faker import Faker
from datetime import datetime, timedelta
from models import db, POHeader, POLine, ASNHeader, ASNLine

fake = Faker()

class DataGenerator:
    def __init__(self):
        """Initialize data generator"""
        self.fake = fake
        
    def generate_asn_id(self):
        """Generate ASN ID: 5 digit number starting with 0"""
        return f"0{random.randint(1000, 9999)}"
    
    def generate_po_id(self):
        """Generate PO ID: 10 digit number starting with 2"""
        return f"2{random.randint(100000000, 999999999)}"
    
    def generate_pallet_id(self):
        """Generate Pallet ID: 15 digit number starting with 5"""
        return f"5{random.randint(10000000000000, 99999999999999)}"
    
    def generate_supplier_reference(self):
        """Generate supplier reference like abc123"""
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        numbers = ''.join(random.choices('0123456789', k=3))
        return f"{letters}{numbers}"
    
    def create_sample_data(self, num_asns=10, num_pos_per_asn=2, num_pallets_per_po=4):
        """Create comprehensive sample data for all tables"""
        print("Generating sample data...")
        
        # Clear existing data
        ASNLine.query.delete()
        POLine.query.delete()
        ASNHeader.query.delete()
        POHeader.query.delete()
        db.session.commit()
        
        asn_data = []
        po_data = []
        
        for asn_idx in range(num_asns):
            # Generate ASN
            asn_id = self.generate_asn_id()
            supplier_ref = self.generate_supplier_reference()
            
            # Create ASN Header
            asn_header = ASNHeader(
                asn_id=asn_id,
                supplier_reference=supplier_ref,
                last_updated_date=self.fake.date_time_between(start_date='-30d', end_date='now')
            )
            
            asn_data.append({
                'asn_id': asn_id,
                'supplier_reference': supplier_ref,
                'pos': []
            })
            
            db.session.add(asn_header)
            
            # Generate POs for this ASN
            for po_idx in range(num_pos_per_asn):
                po_id = self.generate_po_id()
                
                # Create PO Header
                po_header = POHeader(
                    po_id=po_id,
                    status=random.choice(['inprogress', 'received', 'hold']),
                    last_updated_date=self.fake.date_time_between(start_date='-30d', end_date='now')
                )
                
                po_data.append({
                    'po_id': po_id,
                    'asn_id': asn_id,
                    'pallets': []
                })
                
                db.session.add(po_header)
                
                # Generate Pallets for this PO
                for pallet_idx in range(num_pallets_per_po):
                    pallet_id = self.generate_pallet_id()
                    quantity = random.randint(1, 10)
                    
                    # Create PO Line
                    po_line = POLine(
                        pallet_id=pallet_id,
                        po_id=po_id,
                        asn_id=asn_id,
                        quantity=quantity,
                        last_updated_date=self.fake.date_time_between(start_date='-30d', end_date='now')
                    )
                    
                    # Create ASN Line
                    asn_line = ASNLine(
                        pallet_id=pallet_id,
                        po_id=po_id,
                        asn_id=asn_id,
                        supplier_reference=supplier_ref,
                        quantity=quantity,
                        last_updated_date=self.fake.date_time_between(start_date='-30d', end_date='now')
                    )
                    
                    db.session.add(po_line)
                    db.session.add(asn_line)
                    
                    # Store for reference
                    asn_data[asn_idx]['pos'].append({
                        'po_id': po_id,
                        'pallet_id': pallet_id,
                        'quantity': quantity
                    })
                    
                    po_data[-1]['pallets'].append({
                        'pallet_id': pallet_id,
                        'quantity': quantity
                    })
        
        db.session.commit()
        print(f"Generated {num_asns} ASNs with {num_asns * num_pos_per_asn} POs and {num_asns * num_pos_per_asn * num_pallets_per_po} pallets")
        
        return asn_data, po_data
    
    def create_test_scenarios(self):
        """Create specific test scenarios for each issue type"""
        print("Creating test scenarios...")
        
        # Scenario 1: Missing ASN (ASN exists in header but not in line)
        missing_asn_id = self.generate_asn_id()
        asn_header_only = ASNHeader(
            asn_id=missing_asn_id,
            supplier_reference=self.generate_supplier_reference(),
            last_updated_date=datetime.utcnow()
        )
        db.session.add(asn_header_only)
        
        # Scenario 2: Missing PO (completely missing)
        missing_po_id = self.generate_po_id()
        
        # Scenario 3: Missing Pallet (PO exists but pallet missing)
        existing_po_id = self.generate_po_id()
        missing_pallet_id = self.generate_pallet_id()
        existing_asn_id = self.generate_asn_id()
        
        # Create PO header for missing pallet scenario
        po_header = POHeader(
            po_id=existing_po_id,
            status='inprogress',
            last_updated_date=datetime.utcnow()
        )
        db.session.add(po_header)
        
        # Create ASN header for missing pallet scenario
        asn_header = ASNHeader(
            asn_id=existing_asn_id,
            supplier_reference=self.generate_supplier_reference(),
            last_updated_date=datetime.utcnow()
        )
        db.session.add(asn_header)
        
        # Scenario 4: Quantity Mismatch (same pallet different quantities)
        mismatch_po_id = self.generate_po_id()
        mismatch_asn_id = self.generate_asn_id()
        mismatch_pallet_id = self.generate_pallet_id()
        
        # Create PO header
        po_header_mismatch = POHeader(
            po_id=mismatch_po_id,
            status='inprogress',
            last_updated_date=datetime.utcnow()
        )
        db.session.add(po_header_mismatch)
        
        # Create ASN header
        asn_header_mismatch = ASNHeader(
            asn_id=mismatch_asn_id,
            supplier_reference=self.generate_supplier_reference(),
            last_updated_date=datetime.utcnow()
        )
        db.session.add(asn_header_mismatch)
        
        # Create PO line with quantity 5
        po_line_mismatch = POLine(
            pallet_id=mismatch_pallet_id,
            po_id=mismatch_po_id,
            asn_id=mismatch_asn_id,
            quantity=5,
            last_updated_date=datetime.utcnow()
        )
        db.session.add(po_line_mismatch)
        
        # Create ASN line with quantity 3 (mismatch)
        asn_line_mismatch = ASNLine(
            pallet_id=mismatch_pallet_id,
            po_id=mismatch_po_id,
            asn_id=mismatch_asn_id,
            supplier_reference=asn_header_mismatch.supplier_reference,
            quantity=3,
            last_updated_date=datetime.utcnow()
        )
        db.session.add(asn_line_mismatch)
        
        db.session.commit()
        
        test_scenarios = {
            'missing_asn': {
                'asn_id': missing_asn_id,
                'description': f"ASN {missing_asn_id} is missing from the system"
            },
            'missing_po': {
                'po_id': missing_po_id,
                'description': f"PO {missing_po_id} is not found in the system"
            },
            'missing_pallet': {
                'po_id': existing_po_id,
                'asn_id': existing_asn_id,
                'pallet_id': missing_pallet_id,
                'description': f"Pallet {missing_pallet_id} is missing for PO {existing_po_id} and ASN {existing_asn_id}"
            },
            'quantity_mismatch': {
                'po_id': mismatch_po_id,
                'asn_id': mismatch_asn_id,
                'pallet_id': mismatch_pallet_id,
                'description': f"Quantity mismatch for pallet {mismatch_pallet_id} in PO {mismatch_po_id}"
            }
        }
        
        print("Test scenarios created:")
        for scenario_type, details in test_scenarios.items():
            print(f"  {scenario_type}: {details['description']}")
        
        return test_scenarios
    
    def print_data_summary(self):
        """Print summary of generated data"""
        print("\n=== DATA SUMMARY ===")
        
        asn_headers = ASNHeader.query.count()
        asn_lines = ASNLine.query.count()
        po_headers = POHeader.query.count()
        po_lines = POLine.query.count()
        
        print(f"ASN Headers: {asn_headers}")
        print(f"ASN Lines: {asn_lines}")
        print(f"PO Headers: {po_headers}")
        print(f"PO Lines: {po_lines}")
        
        # Sample data
        print("\n=== SAMPLE ASN DATA ===")
        sample_asns = ASNHeader.query.limit(3).all()
        for asn in sample_asns:
            print(f"ASN: {asn.asn_id}, Supplier: {asn.supplier_reference}")
            asn_lines = ASNLine.query.filter_by(asn_id=asn.asn_id).limit(2).all()
            for line in asn_lines:
                print(f"  Pallet: {line.pallet_id}, PO: {line.po_id}, Qty: {line.quantity}")
        
        print("\n=== SAMPLE PO DATA ===")
        sample_pos = POHeader.query.limit(3).all()
        for po in sample_pos:
            print(f"PO: {po.po_id}, Status: {po.status}")
            po_lines = POLine.query.filter_by(po_id=po.po_id).limit(2).all()
            for line in po_lines:
                print(f"  Pallet: {line.pallet_id}, ASN: {line.asn_id}, Qty: {line.quantity}")
    
    def create_sample_issue_descriptions(self, test_scenarios):
        """Create sample issue descriptions for testing"""
        sample_issues = []
        
        # Missing ASN issues
        asn_id = test_scenarios['missing_asn']['asn_id']
        sample_issues.extend([
            f"Hi, I'm reporting that ASN {asn_id} is missing from our system. Please check.",
            f"ASN {asn_id} not found in WMS. Can you help?",
            f"The ASN {asn_id} seems to be missing. Need assistance."
        ])
        
        # Missing PO issues
        po_id = test_scenarios['missing_po']['po_id']
        sample_issues.extend([
            f"Purchase order {po_id} is missing from the system.",
            f"Cannot find PO {po_id} in WMS. Please investigate.",
            f"PO {po_id} is not interfaced. Need help."
        ])
        
        # Missing Pallet issues
        pallet_details = test_scenarios['missing_pallet']
        sample_issues.extend([
            f"Pallet {pallet_details['pallet_id']} is missing for PO {pallet_details['po_id']}.",
            f"Cannot find pallet {pallet_details['pallet_id']} in ASN {pallet_details['asn_id']}.",
            f"Missing pallet {pallet_details['pallet_id']} for PO {pallet_details['po_id']} and ASN {pallet_details['asn_id']}."
        ])
        
        # Quantity Mismatch issues
        qty_details = test_scenarios['quantity_mismatch']
        sample_issues.extend([
            f"Quantity mismatch for pallet {qty_details['pallet_id']} in PO {qty_details['po_id']}.",
            f"Wrong quantity for pallet {qty_details['pallet_id']} in ASN {qty_details['asn_id']}.",
            f"Quantity difference found in PO {qty_details['po_id']} for pallet {qty_details['pallet_id']}."
        ])
        
        return sample_issues