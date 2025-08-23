import os
from flask import Flask
from dotenv import load_dotenv
import logging

# Import our managers
from manager.database_manager import DatabaseManager
from manager.user_manager import UserManager
from manager.vocabulary_manager import VocabularyManager
from manager.practice_session_manager import PracticeSessionManager
from manager.user_statistics_manager import UserStatisticsManager
from manager.user_progress_manager import UserProgressManager
from manager.auth_manager import AuthManager
from manager.practice_manager import PracticeManager

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
    
    # Initialize managers
    db_manager = DatabaseManager()
    user_manager = UserManager(db_manager)
    vocabulary_manager = VocabularyManager(db_manager)
    practice_session_manager = PracticeSessionManager(db_manager)
    user_statistics_manager = UserStatisticsManager(db_manager)
    user_progress_manager = UserProgressManager(db_manager)
    auth_manager = AuthManager(user_manager)
    practice_manager = PracticeManager(db_manager)
    
    # Store managers in app context for easy access
    app.db_manager = db_manager
    app.user_manager = user_manager
    app.vocabulary_manager = vocabulary_manager
    app.practice_session_manager = practice_session_manager
    app.user_statistics_manager = user_statistics_manager
    app.user_progress_manager = user_progress_manager
    app.auth_manager = auth_manager
    app.practice_manager = practice_manager
    
    # Register blueprint
    app.register_blueprint(flash_card_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8087)