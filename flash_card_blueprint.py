import random
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import logging
import requests
import json
import os
from google.oauth2 import id_token
from google.auth.transport.requests import Request

from manager import auth_manager, practice_manager, practice_session_manager, synonym_game_manager, user_progress_manager

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
        stats = user_progress_manager.get_or_update_weekly_stats(session['user']['id'])
        
        # Get group performance
        group_performance = user_progress_manager.get_user_group_performance(session['user']['id'])
        
        # Get recent sessions
        recent_sessions = practice_session_manager.get_user_sessions(session['user']['id'], limit=5)
        
        # Get synonym game history
        game_history = synonym_game_manager.get_game_history(session['user']['id'], limit=5)
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             group_performance=group_performance,
                             recent_sessions=recent_sessions,
                             game_history=game_history)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', 
                             stats={}, 
                             group_performance=[],
                             recent_sessions=[],
                             game_history=[])

@flash_card_bp.route('/practice')
def practice():
    """Practice session page"""
    if 'user' not in session:
        return redirect(url_for('flash_card.index'))
    
    return render_template('practice.html')

@flash_card_bp.route('/synonym-game')
def synonym_game():
    """Synonym game page"""
    if 'user' not in session:
        return redirect(url_for('flash_card.index'))
    
    return render_template('synonym_game.html')

@flash_card_bp.route('/auth/login')
def login():
    """Redirect to Google OAuth login"""
    redirect_uri = url_for('flash_card.auth_callback', _external=True)
    auth_url = auth_manager.get_google_auth_url(redirect_uri)
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
        session_user = auth_manager.handle_google_callback(google_user_data)
        
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
        session_record = practice_session_manager.create_session(user_id)
        
        # Store session ID in user session
        session['current_session_id'] = session_record['id']
        
        return jsonify({
            'status': 'Session started',
            'session_id': session_record['id'],
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
        
        session_record = practice_session_manager.end_session(
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
            'session_id': session_record['id'],
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
        word_response = practice_manager.get_next_word(user_id)
        
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
        result = practice_manager.submit_answer(
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

@flash_card_bp.route('/api/synonym-game/start', methods=['POST'])
def start_synonym_game():
    """Start a new synonym game"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user']['id']
    
    # Start a new game
    game = synonym_game_manager.start_new_game(user_id)
    
    # Store game ID in session
    session['current_synonym_game_id'] = game['id']
    session['current_synonym_game_round'] = 1
    
    return jsonify({
        'status': 'Game started',
        'game_id': game['id'],
        'played_at': game['played_at'].isoformat()
    })


@flash_card_bp.route('/api/synonym-game/next-round', methods=['GET'])
def get_next_synonym_round():
    """Get the next round of the synonym game"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'current_synonym_game_id' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    try:
        # Get two random synonym pairs
        synonym_pairs = synonym_game_manager.get_random_synonym_pairs(2)
        
        if len(synonym_pairs) < 2:
            return jsonify({'error': 'Not enough synonym data available'}), 404
        
        # Combine all words from both pairs
        all_words = []
        meanings = []
        
        for pair in synonym_pairs:
            all_words.extend(pair['words'])
            meanings.append(pair['meaning'])
        
        # Shuffle the words
        random.shuffle(all_words)
        
        # Prepare response
        round_data = {
            'meanings': meanings,
            'words': all_words
        }
        
        # Store current round data in session for answer checking
        session['current_synonym_round_data'] = {
            'meanings': meanings,
            'words': all_words,
            'correct_mappings': {}
        }
        
        # Create mapping of words to their correct meanings
        for pair in synonym_pairs:
            for word in pair['words']:
                session['current_synonym_round_data']['correct_mappings'][word] = pair['meaning']
        
        return jsonify(round_data)
        
    except Exception as e:
        logger.error(f"Error getting next synonym round: {e}")
        return jsonify({'error': 'Failed to get next round'}), 500

@flash_card_bp.route('/api/synonym-game/submit-round', methods=['POST'])
def submit_synonym_round():
    """Submit answers for a round of the synonym game"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'current_synonym_game_id' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    if 'current_synonym_round_data' not in session:
        return jsonify({'error': 'No active round'}), 400
    
    try:
        data = request.get_json()
        user_answers = data.get('answers', {})  # {word: meaning}
        
        # Get correct mappings
        correct_mappings = session['current_synonym_round_data']['correct_mappings']
        meanings = session['current_synonym_round_data']['meanings']
        
        # Calculate scores for each meaning
        meaning_scores = {meaning: {'correct': 0, 'total': 0} for meaning in meanings}
        
        # Check each answer
        for word, selected_meaning in user_answers.items():
            correct_meaning = correct_mappings.get(word)
            if correct_meaning:
                meaning_scores[correct_meaning]['total'] += 1
                if selected_meaning == correct_meaning:
                    meaning_scores[correct_meaning]['correct'] += 1
        
        # Calculate percentage scores for each meaning
        round_scores = []
        game_id = session['current_synonym_game_id']
        round_number = session.get('current_synonym_game_round', 1)
        
        total_round_score = 0
        for meaning, stats in meaning_scores.items():
            if stats['total'] > 0:
                percentage = (stats['correct'] / stats['total']) * 100
                round_scores.append({
                    'meaning': meaning,
                    'correct': stats['correct'],
                    'total': stats['total'],
                    'percentage': percentage
                })
                
                # Record score in database
                score_record = synonym_game_manager.record_round_score(
                    game_id, round_number, meaning, percentage
                )
                total_round_score += percentage
            else:
                round_scores.append({
                    'meaning': meaning,
                    'correct': 0,
                    'total': 0,
                    'percentage': 0
                })
                
                # Record score in database
                score_record = synonym_game_manager.record_round_score(
                    game_id, round_number, meaning, 0
                )
        
        # Update round number in session
        session['current_synonym_game_round'] = round_number + 1
        
        # Clear current round data
        session.pop('current_synonym_round_data', None)
        
        return jsonify({
            'status': 'Round submitted',
            'scores': round_scores,
            'total_score': total_round_score,
            'max_possible_score': 200  # 100% for each of the 2 meanings
        })
        
    except Exception as e:
        logger.error(f"Error submitting synonym round: {e}")
        return jsonify({'error': 'Failed to submit round'}), 500

@flash_card_bp.route('/api/synonym-game/end', methods=['POST'])
def end_synonym_game():
    """End the current synonym game"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'current_synonym_game_id' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    try:
        game_id = session['current_synonym_game_id']
        
        # Get total game score
        game_details = synonym_game_manager.get_game_details(game_id)
        if game_details:
            total_score = sum(
                score['score'] 
                for round_data in game_details['rounds'] 
                for score in round_data['scores']
            )
        else:
            total_score = 0
        
        # Clear game from session
        session.pop('current_synonym_game_id', None)
        session.pop('current_synonym_game_round', None)
        session.pop('current_synonym_round_data', None)
        
        return jsonify({
            'status': 'Game ended',
            'game_id': game_id,
            'total_score': total_score,
            'max_possible_score': 1000  # 5 rounds * 2 meanings * 100 points each
        })
        
    except Exception as e:
        logger.error(f"Error ending synonym game: {e}")
        return jsonify({'error': 'Failed to end game'}), 500