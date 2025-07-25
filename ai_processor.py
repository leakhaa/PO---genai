import re
import logging
from sentence_transformers import SentenceTransformer
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from config import Config

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        """Initialize AI models for text processing and entity extraction"""
        try:
            # Initialize sentence transformer for text similarity
            self.sentence_model = SentenceTransformer(Config.SENTENCE_TRANSFORMER_MODEL)
            
            # Initialize a simple text classification pipeline
            self.classifier = pipeline("text-classification", 
                                     model="distilbert-base-uncased-finetuned-sst-2-english")
            
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            raise

    def extract_entities(self, text):
        """Extract ASN, PO, and Pallet IDs from text using regex patterns"""
        entities = {
            'asn_id': None,
            'po_id': None,
            'pallet_id': None
        }
        
        # ASN pattern: 5 digits starting with 0
        asn_pattern = r'\b0\d{4}\b'
        asn_match = re.search(asn_pattern, text)
        if asn_match:
            entities['asn_id'] = asn_match.group()
        
        # PO pattern: 10 digits starting with 2
        po_pattern = r'\b2\d{9}\b'
        po_match = re.search(po_pattern, text)
        if po_match:
            entities['po_id'] = po_match.group()
        
        # Pallet pattern: 15 digits starting with 5
        pallet_pattern = r'\b5\d{14}\b'
        pallet_match = re.search(pallet_pattern, text)
        if pallet_match:
            entities['pallet_id'] = pallet_match.group()
        
        return entities

    def classify_issue_type(self, text):
        """Classify the type of issue based on text content"""
        text_lower = text.lower()
        
        # Define keywords for each issue type
        keywords = {
            'missing_asn': ['asn missing', 'asn not found', 'missing asn', 'asn is missing'],
            'missing_po': ['po missing', 'po not found', 'missing po', 'po is missing', 'purchase order missing'],
            'missing_pallet': ['pallet missing', 'pallet not found', 'missing pallet', 'pallet is missing'],
            'quantity_mismatch': ['quantity mismatch', 'qty mismatch', 'quantity difference', 
                                'wrong quantity', 'incorrect quantity', 'quantity issue']
        }
        
        # Score each category
        scores = {}
        for issue_type, keyword_list in keywords.items():
            score = 0
            for keyword in keyword_list:
                if keyword in text_lower:
                    score += 1
            scores[issue_type] = score
        
        # Return the issue type with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'unknown'

    def generate_response_email(self, issue_type, entities, resolution_status, data_snippets=None):
        """Generate email response based on issue type and resolution status"""
        
        templates = {
            'missing_asn': {
                'resolved': f"""
Subject: ASN Issue Resolved - {entities.get('asn_id', 'N/A')}

Dear User,

The ASN {entities.get('asn_id', 'N/A')} has been successfully interfaced into the WMS system.

{data_snippets if data_snippets else ''}

The issue has been resolved successfully.

Best regards,
Automated Warehouse Management System
                """,
                'not_found': f"""
Subject: ASN Interface Request - {entities.get('asn_id', 'N/A')}

Dear SAP Team,

Please trigger ASN interface for ASN ID: {entities.get('asn_id', 'N/A')}

This ASN is currently missing from our WMS system.

Best regards,
Automated Warehouse Management System
                """
            },
            'missing_po': {
                'resolved': f"""
Subject: PO Issue Resolved - {entities.get('po_id', 'N/A')}

Dear User,

The PO {entities.get('po_id', 'N/A')} has been successfully interfaced into the WMS system.

{data_snippets if data_snippets else ''}

All pallet counts and quantities are correct.

Best regards,
Automated Warehouse Management System
                """,
                'not_found': f"""
Subject: PO Interface Request - {entities.get('po_id', 'N/A')}

Dear SAP Team,

Please trigger PO interface for PO ID: {entities.get('po_id', 'N/A')}

This PO is currently missing from our WMS system.

Best regards,
Automated Warehouse Management System
                """
            },
            'missing_pallet': {
                'resolved': f"""
Subject: Pallet Issue Resolved - {entities.get('pallet_id', 'N/A')}

Dear User,

The pallet {entities.get('pallet_id', 'N/A')} has been successfully interfaced into the WMS system.

{data_snippets if data_snippets else ''}

All pallet details have been updated correctly.

Best regards,
Automated Warehouse Management System
                """,
                'request_details': f"""
Subject: Pallet Details Request - {entities.get('pallet_id', 'N/A')}

Dear SAP Team,

Please provide pallet details for:
- Pallet ID: {entities.get('pallet_id', 'N/A')}
- PO ID: {entities.get('po_id', 'N/A')}
- ASN ID: {entities.get('asn_id', 'N/A')}

Please send the details in Excel format.

Best regards,
Automated Warehouse Management System
                """
            },
            'quantity_mismatch': {
                'resolved': f"""
Subject: Quantity Mismatch Issue Resolved

Dear User,

The quantity mismatch issue has been resolved successfully.

{data_snippets if data_snippets else ''}

All quantities have been updated and matched correctly.

Best regards,
Automated Warehouse Management System
                """,
                'request_details': f"""
Subject: Quantity Details Request

Dear SAP Team,

Please provide quantity details for:
- PO ID: {entities.get('po_id', 'N/A')}
- ASN ID: {entities.get('asn_id', 'N/A')}
- Pallet ID: {entities.get('pallet_id', 'N/A')}

There appears to be a quantity mismatch that needs investigation.

Best regards,
Automated Warehouse Management System
                """
            }
        }
        
        if issue_type in templates and resolution_status in templates[issue_type]:
            return templates[issue_type][resolution_status]
        else:
            return f"""
Subject: Issue Update

Dear User,

We are processing your request regarding {issue_type}.

Issue details:
- ASN: {entities.get('asn_id', 'N/A')}
- PO: {entities.get('po_id', 'N/A')}
- Pallet: {entities.get('pallet_id', 'N/A')}

We will update you once the issue is resolved.

Best regards,
Automated Warehouse Management System
            """

    def analyze_text_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        try:
            embeddings1 = self.sentence_model.encode([text1])
            embeddings2 = self.sentence_model.encode([text2])
            
            # Calculate cosine similarity
            similarity = torch.nn.functional.cosine_similarity(
                torch.tensor(embeddings1), 
                torch.tensor(embeddings2)
            ).item()
            
            return similarity
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0