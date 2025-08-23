from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app
import logging
import requests
import json
import os
from google.oauth2 import id_token
from google.auth.transport.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
flash_card_bp = Blueprint('flash_card', __name__, url_prefix='/flash_card')

@flash_card_bp.route('/')
def index():
    """Main dashboard page"""
    # For now, we'll redirect to dashboard if user is logged in
    # In a full implementation, this would be the main landing page
    if 'user' in session:
        return redirect(url_for('flash_card.dashboard'))
    
    return render_template('index.html')

@flash_card_bp.route('/dashboard')
def dashboard():
    """User dashboard with statistics"""
    if 'user' not in session:
        return redirect(url_for('flash_card.index'))
    
    try:
        # Get user statistics
        stats = current_app.user_statistics_manager.get_or_update_weekly_stats(session['user']['id'])
        
        # Get group performance
        group_performance = current_app.user_progress_manager.get_user_group_performance(session['user']['id'])
        
        # Get recent sessions
        recent_sessions = current_app.practice_session_manager.get_user_sessions(session['user']['id'], limit=5)
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             group_performance=group_performance,
                             recent_sessions=recent_sessions)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', 
                             stats={}, 
                             group_performance=[],
                             recent_sessions=[])

@flash_card_bp.route('/practice')
def practice():
    """Practice session page"""
    if 'user' not in session:
        return redirect(url_for('flash_card.index'))
    
    return render_template('practice.html')

@flash_card_bp.route('/auth/login')
def login():
    """Redirect to Google OAuth login"""
    redirect_uri = url_for('flash_card.auth_callback', _external=True)
    auth_url = current_app.auth_manager.get_google_auth_url(redirect_uri)
    return redirect(auth_url)

@flash_card_bp.route('/auth/callback', methods=['POST'])
def auth_callback():
    """Handle Google OAuth callback"""
    # Get the authorization code from the request

    print(request.headers["Referer"])
    try:
        user = id_token.verify_oauth2_token(request.form['credential'], Request(), os.getenv('GOOGLE_CLIENT_ID'))
        # Prepare user data for our system
        google_user_data = {
            'google_id':  user["email"],
            'email': user["email"],
            'given_name': user['given_name'],
            'family_name': user["family_name"],
            'name': user['name'],
            'picture': user['picture']
        }
        
        # Handle authentication and get user data for session
        session_user = current_app.auth_manager.handle_google_callback(google_user_data)
        
        # Store user in session
        session['user'] = session_user
        
        return redirect(url_for('flash_card.dashboard'))
        
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return redirect(url_for('flash_card.index'))

@flash_card_bp.route('/auth/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    return redirect(url_for('flash_card.index'))

@flash_card_bp.route('/api/start_session', methods=['POST'])
def start_practice_session():
    """Start a new practice session"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = session['user']['id']
        session_record = current_app.practice_session_manager.create_session(user_id)
        
        # Store session ID in user session
        session['current_session_id'] = str(session_record['id'])
        
        return jsonify({
            'status': 'Session started',
            'session_id': str(session_record['id']),
            'start_time': session_record['start_time'].isoformat()
        })
    except Exception as e:
        logger.error(f"Error starting practice session: {e}")
        return jsonify({'error': 'Failed to start session'}), 500

@flash_card_bp.route('/api/end_session', methods=['POST'])
def end_practice_session():
    """End the current practice session"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'current_session_id' not in session:
        return jsonify({'error': 'No active session'}), 400
    
    try:
        data = request.get_json()
        session_id = session['current_session_id']
        total_score = data.get('total_score', 0)
        words_attempted = data.get('words_attempted', 0)
        words_correct = data.get('words_correct', 0)
        
        session_record = current_app.practice_session_manager.end_session(
            session_id, 
            total_score, 
            words_attempted, 
            words_correct
        )
        
        # Clear session from user session
        session.pop('current_session_id', None)
        session.pop('practice_state', None)
        
        return jsonify({
            'status': 'Session ended',
            'session_id': str(session_record['id']),
            'total_score': session_record['total_score'],
            'words_attempted': session_record['words_attempted'],
            'words_correct': session_record['words_correct']
        })
    except Exception as e:
        logger.error(f"Error ending practice session: {e}")
        return jsonify({'error': 'Failed to end session'}), 500

@flash_card_bp.route('/api/next_word', methods=['GET'])
def get_next_word():
    """Get the next word for practice based on adaptive difficulty"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = session['user']['id']
        
        # Get next word using practice manager
        word_response = current_app.practice_manager.get_next_word(user_id)
        
        if not word_response:
            return jsonify({'error': 'No words available'}), 404
        
        # Store current word in session for answer checking
        session['current_word'] = {
            'word_id': word_response['word_id'],
            'correct_choice_index': 0  # This will be updated when choices are shuffled
        }
        
        # Since we don't know the correct choice index after shuffling in the manager,
        # we need to find it here
        for i, choice in enumerate(word_response['choices']):
            # In a real implementation, we would have a way to identify the correct choice
            # For now, we'll assume the first choice is correct for our simulated implementation
            if 'is_correct' in choice and choice['is_correct']:
                session['current_word']['correct_choice_index'] = i
                break
            # For the simulated implementation, we'll just use index 0
            session['current_word']['correct_choice_index'] = 0
        
        return jsonify(word_response)
        
    except Exception as e:
        logger.error(f"Error getting next word: {e}")
        return jsonify({'error': 'Failed to get next word'}), 500

@flash_card_bp.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit an answer and update user progress"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'current_word' not in session:
        return jsonify({'error': 'No active word'}), 400
    
    try:
        data = request.get_json()
        selected_choice_index = data.get('selected_choice_index')
        time_taken = data.get('time_taken', 0)  # in seconds
        
        # Get session ID if available
        session_id = session.get('current_session_id')
        
        # Submit answer using practice manager
        result = current_app.practice_manager.submit_answer(
            user_id=session['user']['id'],
            word_id=session['current_word']['word_id'],
            selected_choice_index=selected_choice_index,
            correct_choice_index=session['current_word']['correct_choice_index'],
            time_taken=time_taken,
            session_id=session_id
        )
        
        # Clear current word from session
        session.pop('current_word', None)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return jsonify({'error': 'Failed to submit answer'}), 500