#!/usr/bin/env python3
"""
Warehouse Management AI Automation System - Startup Script
This script initializes the system and starts the Flask application.
"""

import os
import sys
import logging
from flask import Flask

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('warehouse_management.log')
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'sqlalchemy',
        'flask_sqlalchemy',
        'faker',
        'pandas',
        'openpyxl',
        'transformers',
        'torch',
        'sentence_transformers',
        'python_dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def initialize_system():
    """Initialize the system with sample data"""
    try:
        from app import app, create_tables
        from data_generator import DataGenerator
        
        print("🔄 Initializing database...")
        with app.app_context():
            create_tables()
            
            # Check if we need to generate sample data
            from models import ASNHeader
            if ASNHeader.query.count() == 0:
                print("🔄 Generating sample data...")
                data_generator = DataGenerator()
                data_generator.create_sample_data(num_asns=5, num_pos_per_asn=2, num_pallets_per_po=3)
                data_generator.create_test_scenarios()
                data_generator.print_data_summary()
                print("✅ Sample data generated successfully!")
            else:
                print("✅ Existing data found, skipping sample data generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return False

def print_startup_info():
    """Print startup information and instructions"""
    print("=" * 80)
    print("🏭 WAREHOUSE MANAGEMENT AI AUTOMATION SYSTEM")
    print("=" * 80)
    print("🚀 System started successfully!")
    print()
    print("📊 Features:")
    print("   • AI-powered issue classification and entity extraction")
    print("   • Automated email communication with users and SAP")
    print("   • Real-time ticket processing and resolution")
    print("   • Web dashboard for monitoring and manual testing")
    print()
    print("🌐 Access Points:")
    print("   • Web Interface: http://localhost:5000")
    print("   • API Documentation: http://localhost:5000/health")
    print("   • Sample Issues: Available on the web interface")
    print()
    print("🧪 Testing:")
    print("   • Run automated tests: python test_system.py")
    print("   • Generate sample data: Click button on web interface")
    print("   • Monitor logs: tail -f warehouse_management.log")
    print()
    print("🤖 AI Models:")
    print("   • Sentence Transformer: all-MiniLM-L6-v2")
    print("   • Classification: DistilBERT")
    print("   • Entity Extraction: Regex + NLP")
    print()
    print("=" * 80)

def main():
    """Main startup function"""
    print("🚀 Starting Warehouse Management AI Automation System...")
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize system
    if not initialize_system():
        sys.exit(1)
    
    # Print startup info
    print_startup_info()
    
    try:
        # Import and run the Flask app
        from app import app
        
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Starting Flask application on port {port}")
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        logger.info("Application shutdown requested by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        logger.error(f"Application startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()