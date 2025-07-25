import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///warehouse_management.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', 'your_email@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_app_password')
    
    # SAP Email Configuration
    SAP_EMAIL = os.getenv('SAP_EMAIL', 'sap_team@company.com')
    
    # AI Model Configuration
    HUGGINGFACE_MODEL = os.getenv('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-medium')
    SENTENCE_TRANSFORMER_MODEL = os.getenv('SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'