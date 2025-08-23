import os
import logging
from urllib.parse import urlencode

from flask import session
from manager.user_manager import UserManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, user_manager=None):
        self.user_manager = user_manager or UserManager()
    
    def get_google_auth_url(self, redirect_uri):
        """Generate Google OAuth URL"""
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        
        # Build Google OAuth URL
        google_auth_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            'client_id': google_client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline'
        }
        
        auth_url = f"{google_auth_url}?{urlencode(params)}"
        return auth_url
    
    def handle_google_callback(self, google_user_data):
        """Handle Google OAuth callback and get or create user"""
        try:
            print(google_user_data)
            # Get or create user in database
            user = self.user_manager.get_or_create_user(
                google_user_data['google_id'],
                google_user_data['email'],
                google_user_data['given_name'],
                google_user_data['family_name'],
                google_user_data['name'],
                google_user_data['picture']
            )
            
            # Format user data for session storage
            session_user = {
                'id': str(user['id']),
                'google_id': user['google_id'],
                'email': user['email'],
                'name': user['name'],
                'family_name': user['family_name'],
                'given_name': user['given_name'],
                'picture': user['picture_url']
            }
            
            session['user'] = {
                'id': str(user['id']),
                'google_id': user['google_id'],
                'email': user['email'],
                'name': user['name'],
                'family_name': user['family_name'],
                'given_name': user['given_name'],
                'picture': user['picture_url']
            }
            
            return session_user
            
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            raise