#!/usr/bin/env python3
"""
Test script for the Warehouse Management AI Automation System
This script demonstrates all four scenarios with sample data.
"""

import sys
import time
import requests
import json
from datetime import datetime

class SystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_connection(self):
        """Test if the system is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ System is running and healthy")
                return True
            else:
                print(f"❌ System health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to system: {e}")
            return False
    
    def generate_sample_data(self):
        """Generate sample data for testing"""
        print("\n🔄 Generating sample data...")
        try:
            response = self.session.post(f"{self.base_url}/api/generate-sample-data")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sample data generated successfully")
                print(f"   - ASNs: {data.get('asn_count', 0)}")
                print(f"   - POs: {data.get('po_count', 0)}")
                return data.get('test_scenarios', {})
            else:
                print(f"❌ Failed to generate sample data: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error generating sample data: {e}")
            return {}
    
    def submit_issue(self, user_email, issue_description, scenario_name):
        """Submit an issue and return the response"""
        print(f"\n📝 Testing {scenario_name}...")
        print(f"   Issue: {issue_description}")
        
        try:
            payload = {
                "user_email": user_email,
                "issue_description": issue_description
            }
            
            response = self.session.post(
                f"{self.base_url}/api/submit-issue",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Issue submitted successfully")
                    print(f"   - Ticket ID: {data.get('ticket_id')}")
                    print(f"   - Issue Type: {data.get('issue_type')}")
                    print(f"   - Extracted Entities: {data.get('entities')}")
                    return data
                else:
                    print(f"❌ Issue submission failed: {data.get('error')}")
                    return None
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error submitting issue: {e}")
            return None
    
    def wait_for_processing(self, ticket_id, max_wait=30):
        """Wait for ticket processing to complete"""
        print(f"⏳ Waiting for ticket {ticket_id} to be processed...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = self.session.get(f"{self.base_url}/api/ticket/{ticket_id}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        ticket = data.get('ticket')
                        status = ticket.get('status')
                        print(f"   Current status: {status}")
                        
                        if status in ['resolved', 'closed']:
                            print(f"✅ Ticket {ticket_id} processed successfully")
                            return ticket
                        elif status == 'in_progress':
                            time.sleep(2)
                            continue
                        else:
                            print(f"⚠️  Ticket status: {status}")
                            return ticket
                    else:
                        print(f"❌ Error getting ticket: {data.get('error')}")
                        return None
                else:
                    print(f"❌ HTTP Error getting ticket: {response.status_code}")
                    return None
            except Exception as e:
                print(f"❌ Error checking ticket status: {e}")
                return None
        
        print(f"⏰ Timeout waiting for ticket {ticket_id}")
        return None
    
    def test_scenario_1_missing_asn(self, test_scenarios):
        """Test Scenario 1: Missing ASN"""
        print("\n" + "="*60)
        print("🧪 SCENARIO 1: MISSING ASN")
        print("="*60)
        
        if 'missing_asn' not in test_scenarios:
            print("❌ Missing ASN test scenario not available")
            return
        
        asn_id = test_scenarios['missing_asn']['asn_id']
        issue_description = f"Hi, ASN {asn_id} is missing from our WMS system. Please check and resolve."
        
        result = self.submit_issue(
            user_email="warehouse.user@company.com",
            issue_description=issue_description,
            scenario_name="Missing ASN"
        )
        
        if result:
            ticket = self.wait_for_processing(result['ticket_id'])
            if ticket:
                print(f"📊 Final Status: {ticket.get('status')}")
                print(f"📅 Resolved: {ticket.get('resolved_date', 'Not resolved')}")
    
    def test_scenario_2_missing_po(self, test_scenarios):
        """Test Scenario 2: Missing PO"""
        print("\n" + "="*60)
        print("🧪 SCENARIO 2: MISSING PO")
        print("="*60)
        
        if 'missing_po' not in test_scenarios:
            print("❌ Missing PO test scenario not available")
            return
        
        po_id = test_scenarios['missing_po']['po_id']
        issue_description = f"Purchase order {po_id} is not found in our WMS. Please investigate and interface it."
        
        result = self.submit_issue(
            user_email="po.manager@company.com",
            issue_description=issue_description,
            scenario_name="Missing PO"
        )
        
        if result:
            ticket = self.wait_for_processing(result['ticket_id'])
            if ticket:
                print(f"📊 Final Status: {ticket.get('status')}")
                print(f"📅 Resolved: {ticket.get('resolved_date', 'Not resolved')}")
    
    def test_scenario_3_missing_pallet(self, test_scenarios):
        """Test Scenario 3: Missing Pallet"""
        print("\n" + "="*60)
        print("🧪 SCENARIO 3: MISSING PALLET")
        print("="*60)
        
        if 'missing_pallet' not in test_scenarios:
            print("❌ Missing Pallet test scenario not available")
            return
        
        scenario = test_scenarios['missing_pallet']
        po_id = scenario['po_id']
        asn_id = scenario['asn_id']
        pallet_id = scenario['pallet_id']
        
        issue_description = f"Pallet {pallet_id} is missing for PO {po_id} and ASN {asn_id}. Please provide the pallet details."
        
        result = self.submit_issue(
            user_email="pallet.supervisor@company.com",
            issue_description=issue_description,
            scenario_name="Missing Pallet"
        )
        
        if result:
            ticket = self.wait_for_processing(result['ticket_id'])
            if ticket:
                print(f"📊 Final Status: {ticket.get('status')}")
                print(f"📅 Resolved: {ticket.get('resolved_date', 'Not resolved')}")
    
    def test_scenario_4_quantity_mismatch(self, test_scenarios):
        """Test Scenario 4: Quantity Mismatch"""
        print("\n" + "="*60)
        print("🧪 SCENARIO 4: QUANTITY MISMATCH")
        print("="*60)
        
        if 'quantity_mismatch' not in test_scenarios:
            print("❌ Quantity Mismatch test scenario not available")
            return
        
        scenario = test_scenarios['quantity_mismatch']
        po_id = scenario['po_id']
        asn_id = scenario['asn_id']
        pallet_id = scenario['pallet_id']
        
        issue_description = f"There's a quantity mismatch for pallet {pallet_id} in PO {po_id}. The quantities don't match between PO and ASN {asn_id}."
        
        result = self.submit_issue(
            user_email="quality.control@company.com",
            issue_description=issue_description,
            scenario_name="Quantity Mismatch"
        )
        
        if result:
            ticket = self.wait_for_processing(result['ticket_id'])
            if ticket:
                print(f"📊 Final Status: {ticket.get('status')}")
                print(f"📅 Resolved: {ticket.get('resolved_date', 'Not resolved')}")
    
    def test_ai_entity_extraction(self):
        """Test AI entity extraction with various inputs"""
        print("\n" + "="*60)
        print("🧪 AI ENTITY EXTRACTION TESTS")
        print("="*60)
        
        test_cases = [
            "ASN 01234 is missing from the system",
            "PO 2123456789 not found in WMS",
            "Pallet 512345678901234 is missing for PO 2987654321",
            "Quantity mismatch in ASN 09876 for pallet 543210987654321",
            "Issue with PO 2555666777 and ASN 04321 - pallet 567890123456789 has wrong qty"
        ]
        
        for i, description in enumerate(test_cases, 1):
            print(f"\n🔍 Test Case {i}: {description}")
            
            result = self.submit_issue(
                user_email=f"test.user{i}@company.com",
                issue_description=description,
                scenario_name=f"AI Test {i}"
            )
            
            if result:
                entities = result.get('entities', {})
                issue_type = result.get('issue_type', 'unknown')
                
                print(f"   🤖 AI Classification: {issue_type}")
                print(f"   🏷️  Extracted Entities:")
                print(f"      - ASN: {entities.get('asn_id', 'None')}")
                print(f"      - PO: {entities.get('po_id', 'None')}")
                print(f"      - Pallet: {entities.get('pallet_id', 'None')}")
    
    def get_system_stats(self):
        """Get system statistics"""
        print("\n" + "="*60)
        print("📊 SYSTEM STATISTICS")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/tickets")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    tickets = data.get('tickets', [])
                    
                    total_tickets = len(tickets)
                    status_counts = {}
                    type_counts = {}
                    
                    for ticket in tickets:
                        status = ticket.get('status', 'unknown')
                        issue_type = ticket.get('issue_type', 'unknown')
                        
                        status_counts[status] = status_counts.get(status, 0) + 1
                        type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
                    
                    print(f"📈 Total Tickets: {total_tickets}")
                    print(f"📊 By Status:")
                    for status, count in status_counts.items():
                        print(f"   - {status.title()}: {count}")
                    
                    print(f"📊 By Type:")
                    for issue_type, count in type_counts.items():
                        print(f"   - {issue_type.replace('_', ' ').title()}: {count}")
                    
                    return tickets
                else:
                    print(f"❌ Error getting tickets: {data.get('error')}")
                    return []
            else:
                print(f"❌ HTTP Error getting tickets: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting system stats: {e}")
            return []
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 WAREHOUSE MANAGEMENT AI AUTOMATION - COMPREHENSIVE TEST")
        print("="*80)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test connection
        if not self.test_connection():
            print("❌ Cannot proceed with tests - system not available")
            return
        
        # Generate sample data
        test_scenarios = self.generate_sample_data()
        if not test_scenarios:
            print("❌ Cannot proceed with tests - no test scenarios available")
            return
        
        # Wait a moment for data to be ready
        time.sleep(2)
        
        # Run all scenario tests
        self.test_scenario_1_missing_asn(test_scenarios)
        self.test_scenario_2_missing_po(test_scenarios)
        self.test_scenario_3_missing_pallet(test_scenarios)
        self.test_scenario_4_quantity_mismatch(test_scenarios)
        
        # Test AI capabilities
        self.test_ai_entity_extraction()
        
        # Wait for all processing to complete
        print("\n⏳ Waiting for all tickets to be processed...")
        time.sleep(10)
        
        # Get final statistics
        tickets = self.get_system_stats()
        
        print("\n" + "="*80)
        print("✅ COMPREHENSIVE TEST COMPLETED")
        print("="*80)
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎫 Total tickets created: {len(tickets)}")
        print(f"🌐 Access the web interface at: {self.base_url}")
        print("="*80)

def main():
    """Main function"""
    base_url = "http://localhost:5000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🎯 Testing system at: {base_url}")
    
    tester = SystemTester(base_url)
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()