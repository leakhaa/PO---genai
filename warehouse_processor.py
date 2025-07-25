import logging
import time
from datetime import datetime
from models import db, POHeader, POLine, ASNHeader, ASNLine, IssueTicket
from ai_processor import AIProcessor
from email_service import EmailService
import pandas as pd

logger = logging.getLogger(__name__)

class WarehouseProcessor:
    def __init__(self):
        """Initialize warehouse processor with AI and email services"""
        self.ai_processor = AIProcessor()
        self.email_service = EmailService()

    def process_issue_ticket(self, ticket_id, user_email, issue_description):
        """Main method to process incoming issue tickets"""
        try:
            logger.info(f"Processing ticket {ticket_id}")
            
            # Extract entities using AI
            entities = self.ai_processor.extract_entities(issue_description)
            
            # Classify issue type using AI
            issue_type = self.ai_processor.classify_issue_type(issue_description)
            
            # Create issue ticket record
            ticket = IssueTicket(
                ticket_id=ticket_id,
                user_email=user_email,
                issue_description=issue_description,
                issue_type=issue_type,
                status='in_progress',
                asn_id=entities.get('asn_id'),
                po_id=entities.get('po_id'),
                pallet_id=entities.get('pallet_id')
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            # Route to appropriate scenario handler
            if issue_type == 'missing_asn':
                self._handle_missing_asn(ticket, entities)
            elif issue_type == 'missing_po':
                self._handle_missing_po(ticket, entities)
            elif issue_type == 'missing_pallet':
                self._handle_missing_pallet(ticket, entities)
            elif issue_type == 'quantity_mismatch':
                self._handle_quantity_mismatch(ticket, entities)
            else:
                self._handle_unknown_issue(ticket, entities)
                
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_id}: {e}")
            raise

    def _handle_missing_asn(self, ticket, entities):
        """Scenario 1: Handle missing ASN"""
        logger.info(f"Handling missing ASN for ticket {ticket.ticket_id}")
        
        asn_id = entities.get('asn_id')
        if not asn_id:
            logger.warning("No ASN ID found in the issue description")
            return
        
        # Check ASN header and line tables
        asn_header = ASNHeader.query.filter_by(asn_id=asn_id).first()
        asn_lines = ASNLine.query.filter_by(asn_id=asn_id).all()
        
        if asn_header and asn_lines:
            # ASN is present - send success email to user
            data_snippets = self._format_asn_data(asn_header, asn_lines, highlight_asn=asn_id)
            email_body = self.ai_processor.generate_response_email(
                'missing_asn', entities, 'resolved', data_snippets
            )
            
            self.email_service.send_to_user(
                ticket.user_email,
                f"ASN Issue Resolved - {asn_id}",
                email_body
            )
            
            self._close_ticket(ticket, 'resolved')
            
        else:
            # ASN is missing - request from SAP
            email_body = self.ai_processor.generate_response_email(
                'missing_asn', entities, 'not_found'
            )
            
            self.email_service.send_to_sap(
                f"ASN Interface Request - {asn_id}",
                email_body
            )
            
            # Wait and check again (in real implementation, this would be event-driven)
            self._wait_and_recheck_asn(ticket, entities, asn_id)

    def _handle_missing_po(self, ticket, entities):
        """Scenario 2: Handle missing PO"""
        logger.info(f"Handling missing PO for ticket {ticket.ticket_id}")
        
        po_id = entities.get('po_id')
        if not po_id:
            logger.warning("No PO ID found in the issue description")
            return
        
        # Check PO header, PO line, and ASN line tables
        po_header = POHeader.query.filter_by(po_id=po_id).first()
        po_lines = POLine.query.filter_by(po_id=po_id).all()
        asn_lines = ASNLine.query.filter_by(po_id=po_id).all()
        
        if po_header and po_lines:
            # PO exists - verify pallet count and quantities
            if self._verify_po_data_consistency(po_lines, asn_lines):
                # All correct - send success email
                data_snippets = self._format_po_data(po_header, po_lines, highlight_po=po_id)
                email_body = self.ai_processor.generate_response_email(
                    'missing_po', entities, 'resolved', data_snippets
                )
                
                self.email_service.send_to_user(
                    ticket.user_email,
                    f"PO Issue Resolved - {po_id}",
                    email_body
                )
                
                self._close_ticket(ticket, 'resolved')
            else:
                # Data inconsistency - handle based on type
                self._handle_po_data_inconsistency(ticket, entities, po_lines, asn_lines)
        else:
            # PO is missing - request from SAP
            email_body = self.ai_processor.generate_response_email(
                'missing_po', entities, 'not_found'
            )
            
            self.email_service.send_to_sap(
                f"PO Interface Request - {po_id}",
                email_body
            )
            
            self._wait_and_recheck_po(ticket, entities, po_id)

    def _handle_missing_pallet(self, ticket, entities):
        """Scenario 3: Handle missing pallet"""
        logger.info(f"Handling missing pallet for ticket {ticket.ticket_id}")
        
        pallet_id = entities.get('pallet_id')
        po_id = entities.get('po_id')
        asn_id = entities.get('asn_id')
        
        if not pallet_id:
            logger.warning("No Pallet ID found in the issue description")
            return
        
        # Check pallet in PO line and ASN line
        po_pallet = POLine.query.filter_by(pallet_id=pallet_id).first()
        asn_pallet = ASNLine.query.filter_by(pallet_id=pallet_id).first()
        
        if po_pallet and asn_pallet:
            # Pallet is present - send success email
            data_snippets = self._format_pallet_data(po_pallet, asn_pallet, highlight_pallet=pallet_id)
            email_body = self.ai_processor.generate_response_email(
                'missing_pallet', entities, 'resolved', data_snippets
            )
            
            self.email_service.send_to_user(
                ticket.user_email,
                f"Pallet Issue Resolved - {pallet_id}",
                email_body
            )
            
            self._close_ticket(ticket, 'resolved')
        else:
            # Pallet is missing - request details from SAP
            email_body = self.ai_processor.generate_response_email(
                'missing_pallet', entities, 'request_details'
            )
            
            self.email_service.send_to_sap(
                f"Pallet Details Request - {pallet_id}",
                email_body
            )
            
            # In real implementation, this would wait for Excel file response
            self._simulate_sap_response_and_update_pallet(ticket, entities)

    def _handle_quantity_mismatch(self, ticket, entities):
        """Scenario 4: Handle quantity mismatch"""
        logger.info(f"Handling quantity mismatch for ticket {ticket.ticket_id}")
        
        # Request details from SAP for given parameters
        email_body = self.ai_processor.generate_response_email(
            'quantity_mismatch', entities, 'request_details'
        )
        
        self.email_service.send_to_sap(
            "Quantity Details Request",
            email_body
        )
        
        # Simulate receiving and processing Excel file
        self._simulate_quantity_mismatch_resolution(ticket, entities)

    def _handle_unknown_issue(self, ticket, entities):
        """Handle unknown or unclassified issues"""
        logger.warning(f"Unknown issue type for ticket {ticket.ticket_id}")
        
        email_body = f"""
        Dear User,
        
        We received your issue report but could not automatically classify the issue type.
        
        Issue Description: {ticket.issue_description}
        
        Our team will review this manually and get back to you soon.
        
        Best regards,
        Automated Warehouse Management System
        """
        
        self.email_service.send_to_user(
            ticket.user_email,
            f"Issue Under Review - {ticket.ticket_id}",
            email_body
        )

    def _verify_po_data_consistency(self, po_lines, asn_lines):
        """Verify if PO and ASN data are consistent"""
        try:
            # Count pallets and quantities
            po_pallet_count = len(po_lines)
            asn_pallet_count = len(asn_lines)
            
            po_total_qty = sum(line.quantity for line in po_lines)
            asn_total_qty = sum(line.quantity for line in asn_lines)
            
            return (po_pallet_count == asn_pallet_count and 
                    po_total_qty == asn_total_qty)
        except Exception as e:
            logger.error(f"Error verifying PO data consistency: {e}")
            return False

    def _handle_po_data_inconsistency(self, ticket, entities, po_lines, asn_lines):
        """Handle PO data inconsistency"""
        po_pallets = {line.pallet_id for line in po_lines}
        asn_pallets = {line.pallet_id for line in asn_lines}
        
        missing_pallets = po_pallets - asn_pallets
        
        if missing_pallets:
            # Handle as missing pallet scenario
            entities['pallet_id'] = list(missing_pallets)[0]  # Take first missing pallet
            self._handle_missing_pallet(ticket, entities)
        else:
            # Handle as quantity mismatch
            self._handle_quantity_mismatch(ticket, entities)

    def _wait_and_recheck_asn(self, ticket, entities, asn_id):
        """Wait for SAP response and recheck ASN (simplified simulation)"""
        # In real implementation, this would be event-driven
        time.sleep(5)  # Simulate waiting
        
        # Simulate SAP triggering the ASN
        self._simulate_sap_asn_trigger(asn_id)
        
        # Recheck
        asn_header = ASNHeader.query.filter_by(asn_id=asn_id).first()
        if asn_header:
            email_body = f"""
            Dear User,
            
            The ASN {asn_id} has been successfully interfaced into the WMS system.
            The issue has been resolved.
            
            Best regards,
            Automated Warehouse Management System
            """
            
            self.email_service.send_to_user(
                ticket.user_email,
                f"ASN Issue Resolved - {asn_id}",
                email_body
            )
            
            self._close_ticket(ticket, 'resolved')

    def _wait_and_recheck_po(self, ticket, entities, po_id):
        """Wait for SAP response and recheck PO (simplified simulation)"""
        # Similar to ASN recheck
        time.sleep(5)
        
        # Simulate SAP triggering the PO
        self._simulate_sap_po_trigger(po_id)
        
        # Recheck and notify user
        po_header = POHeader.query.filter_by(po_id=po_id).first()
        if po_header:
            self._close_ticket(ticket, 'resolved')

    def _simulate_sap_response_and_update_pallet(self, ticket, entities):
        """Simulate SAP Excel response and update pallet data"""
        # In real implementation, this would parse actual Excel file
        pallet_data = [
            {
                'pallet_id': entities.get('pallet_id'),
                'po_id': entities.get('po_id'),
                'asn_id': entities.get('asn_id'),
                'quantity': 5,
                'supplier_reference': 'ABC123'
            }
        ]
        
        # Add to database
        for data in pallet_data:
            po_line = POLine(
                pallet_id=data['pallet_id'],
                po_id=data['po_id'],
                asn_id=data['asn_id'],
                quantity=data['quantity']
            )
            
            asn_line = ASNLine(
                pallet_id=data['pallet_id'],
                po_id=data['po_id'],
                asn_id=data['asn_id'],
                supplier_reference=data['supplier_reference'],
                quantity=data['quantity']
            )
            
            db.session.add(po_line)
            db.session.add(asn_line)
        
        db.session.commit()
        
        # Send success email
        email_body = f"""
        Dear User,
        
        The pallet {entities.get('pallet_id')} has been successfully interfaced into the WMS system.
        All pallet details have been updated correctly.
        
        Best regards,
        Automated Warehouse Management System
        """
        
        self.email_service.send_to_user(
            ticket.user_email,
            f"Pallet Issue Resolved - {entities.get('pallet_id')}",
            email_body
        )
        
        self._close_ticket(ticket, 'resolved')

    def _simulate_quantity_mismatch_resolution(self, ticket, entities):
        """Simulate quantity mismatch resolution"""
        # This would involve parsing Excel file and updating quantities
        email_body = f"""
        Dear User,
        
        The quantity mismatch issue has been resolved successfully.
        All quantities have been updated and matched correctly.
        
        Best regards,
        Automated Warehouse Management System
        """
        
        self.email_service.send_to_user(
            ticket.user_email,
            "Quantity Mismatch Issue Resolved",
            email_body
        )
        
        self._close_ticket(ticket, 'resolved')

    def _simulate_sap_asn_trigger(self, asn_id):
        """Simulate SAP triggering ASN interface"""
        asn_header = ASNHeader(
            asn_id=asn_id,
            supplier_reference=f"SUP{asn_id}"
        )
        db.session.add(asn_header)
        db.session.commit()

    def _simulate_sap_po_trigger(self, po_id):
        """Simulate SAP triggering PO interface"""
        po_header = POHeader(
            po_id=po_id,
            status='inprogress'
        )
        db.session.add(po_header)
        db.session.commit()

    def _format_asn_data(self, asn_header, asn_lines, highlight_asn=None):
        """Format ASN data for email snippets"""
        data = []
        
        # Add header data
        data.append({
            'asn_id': asn_header.asn_id,
            'supplier_reference': asn_header.supplier_reference,
            'last_updated_date': asn_header.last_updated_date
        })
        
        # Add line data
        for line in asn_lines:
            data.append({
                'pallet_id': line.pallet_id,
                'po_id': line.po_id,
                'asn_id': line.asn_id,
                'quantity': line.quantity
            })
        
        return self.email_service.format_data_snippets(
            data, 'ASN', highlight_fields=['asn_id'] if highlight_asn else None
        )

    def _format_po_data(self, po_header, po_lines, highlight_po=None):
        """Format PO data for email snippets"""
        data = []
        
        # Add header data
        data.append({
            'po_id': po_header.po_id,
            'status': po_header.status,
            'last_updated_date': po_header.last_updated_date
        })
        
        # Add line data
        for line in po_lines:
            data.append({
                'pallet_id': line.pallet_id,
                'po_id': line.po_id,
                'asn_id': line.asn_id,
                'quantity': line.quantity
            })
        
        return self.email_service.format_data_snippets(
            data, 'PO', highlight_fields=['po_id'] if highlight_po else None
        )

    def _format_pallet_data(self, po_pallet, asn_pallet, highlight_pallet=None):
        """Format pallet data for email snippets"""
        data = [
            {
                'table': 'PO_LINE',
                'pallet_id': po_pallet.pallet_id,
                'po_id': po_pallet.po_id,
                'asn_id': po_pallet.asn_id,
                'quantity': po_pallet.quantity
            },
            {
                'table': 'ASN_LINE',
                'pallet_id': asn_pallet.pallet_id,
                'po_id': asn_pallet.po_id,
                'asn_id': asn_pallet.asn_id,
                'quantity': asn_pallet.quantity
            }
        ]
        
        return self.email_service.format_data_snippets(
            data, 'PALLET', highlight_fields=['pallet_id'] if highlight_pallet else None
        )

    def _close_ticket(self, ticket, status):
        """Close the issue ticket"""
        ticket.status = status
        ticket.resolved_date = datetime.utcnow()
        db.session.commit()
        logger.info(f"Ticket {ticket.ticket_id} closed with status: {status}")