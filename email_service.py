import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import io
from config import Config

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.EMAIL_USERNAME
        self.password = Config.EMAIL_PASSWORD
        self.sap_email = Config.SAP_EMAIL

    def send_email(self, to_email, subject, body, attachments=None):
        """Send email with optional attachments"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)

            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.username, self.password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def _add_attachment(self, msg, attachment):
        """Add attachment to email message"""
        try:
            if isinstance(attachment, dict):
                filename = attachment.get('filename', 'attachment.txt')
                content = attachment.get('content', '')
                
                # Create attachment
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
                
        except Exception as e:
            logger.error(f"Failed to add attachment: {e}")

    def send_to_user(self, user_email, subject, body, data_snippets=None):
        """Send email to user with data snippets"""
        full_body = body
        
        if data_snippets:
            full_body += "\n\nData Snippets:\n"
            full_body += data_snippets
        
        return self.send_email(user_email, subject, full_body)

    def send_to_sap(self, subject, body):
        """Send email to SAP team"""
        return self.send_email(self.sap_email, subject, body)

    def format_data_snippets(self, data, table_name, highlight_fields=None):
        """Format database data as readable snippets"""
        try:
            if not data:
                return "No data found."
            
            snippet = f"\n=== {table_name.upper()} TABLE ===\n"
            
            for record in data:
                snippet += "-" * 50 + "\n"
                for key, value in record.items():
                    if highlight_fields and key in highlight_fields:
                        snippet += f">>> {key.upper()}: {value} <<<\n"
                    else:
                        snippet += f"{key}: {value}\n"
                snippet += "-" * 50 + "\n"
            
            return snippet
            
        except Exception as e:
            logger.error(f"Error formatting data snippets: {e}")
            return "Error formatting data snippets."

    def create_excel_attachment(self, data, filename):
        """Create Excel attachment from data"""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Create Excel file in memory
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            
            excel_buffer.seek(0)
            
            return {
                'filename': filename,
                'content': excel_buffer.getvalue()
            }
            
        except Exception as e:
            logger.error(f"Error creating Excel attachment: {e}")
            return None

    def parse_excel_from_email(self, excel_file_path):
        """Parse Excel file received from SAP team"""
        try:
            df = pd.read_excel(excel_file_path)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            return None