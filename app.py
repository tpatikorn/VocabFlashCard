import os
from flask import Flask
from dotenv import load_dotenv
import logging

# Import blueprint
from flash_card_blueprint import flash_card_bp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key_for_development')
        
    # Register blueprint
    app.register_blueprint(flash_card_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8087)