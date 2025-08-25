import random
import logging
from manager import user_word_level_manager
from manager import word_manager
from manager import vocabulary_manager
from manager import user_progress_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_next_word(user_id):
    """Get the next word for practice based on adaptive difficulty"""
    try:
        # Get user's word levels
        words_with_levels = user_word_level_manager.get_user_words_with_levels(user_id)
        
        # Filter to words that have been practiced at least once or are at level 0
        # For new users, we'll select words at level 0
        unpracticed_words = [w for w in words_with_levels if w['level'] == 0]
        practiced_words = [w for w in words_with_levels if w['level'] > 0]
        
        # Select a word based on our adaptive algorithm:
        # 1. If user has unpracticed words, select from those first
        # 2. Otherwise, select based on a weighted distribution favoring lower levels
        if unpracticed_words:
            selected_word = random.choice(unpracticed_words)
        elif practiced_words:
            # Weighted selection - words at lower levels are more likely to be selected
            # This is a simplified version of the adaptive algorithm
            levels = [w['level'] for w in practiced_words]
            max_level = max(levels) if levels else 0
            
            # Create weights that favor lower levels
            weights = [max_level - w['level'] + 1 for w in practiced_words]
            selected_word = random.choices(practiced_words, weights=weights)[0]
        else:
            # Fallback - select any word
            if words_with_levels:
                selected_word = random.choice(words_with_levels)
            else:
                # If no words in database, return error
                return None
        
        # Get the word details
        word_details = word_manager.get_word_by_id(selected_word['word_id'])
        
        if not word_details:
            return None
        
        # Determine difficulty level and time limit based on user's level for this word
        level = selected_word['level']
        
        # Calculate time limit based on level
        # Level 0: No time limit (represented as 0)
        # Level 1: 60 seconds
        # Level 2: 60 seconds
        # Level 3+: 60 seconds - (level - 2) * 5 seconds
        if level == 0:
            time_limit = 0  # No time limit
        elif level in [1, 2]:
            time_limit = 60  # 1 minute
        else:
            time_limit = max(60 - (level - 2) * 5, 10)  # Minimum 10 seconds
        
        # Generate choices based on level
        choices = generate_choices(word_details, level, user_id)
        
        # Format the response
        word_response = {
            'word_id': word_details['id'],
            'word': word_details['word'],
            'part_of_speech': word_details['part_of_speech'],
            'meaning_en': word_details['meaning_en'],
            'meaning_th': word_details['meaning_th'],
            'level': level,
            'time_limit': time_limit,  # seconds (0 = no limit)
            'choices': choices
        }
        
        return word_response
        
    except Exception as e:
        logger.error(f"Error getting next word: {e}")
        raise

def generate_choices(correct_word, level, user_id):
    """Generate multiple choice options based on difficulty level"""
    try:
        # The first choice is always the correct answer
        choices = []
        
        # Format based on level
        if level == 0:
            # Level 0: Show both English and Thai meanings, include hints
            correct_choice = {
                'text_en': correct_word['meaning_en'],
                'text_th': correct_word['meaning_th'],
                'is_correct': True
            }
            choices.append(correct_choice)
            
            # Add distractors (incorrect choices)
            distractors = vocabulary_manager.get_distractors(correct_word, 3)
            for distractor in distractors:
                choices.append({
                    'text_en': distractor['meaning_en'],
                    'text_th': distractor['meaning_th'],
                    'is_correct': False
                })

            # Add hints for level 0 (synonyms and antonyms)
            hints = []
            if correct_word['synonyms']:
                hints.extend([f"Synonym: {s}" for s in correct_word['synonyms'][:2]])
            if correct_word['antonyms']:
                hints.extend([f"Antonym: {a}" for a in correct_word['antonyms'][:2]])
            
        elif level in [1, 2]:
            # Level 1 & 2: Show both English and Thai meanings
            correct_choice = {
                'text_en': correct_word['meaning_en'],
                'text_th': correct_word['meaning_th'],
                'is_correct': True
            }
            choices.append(correct_choice)
            
            # Add distractors
            group_name = get_group_name_for_word(correct_word['id'])
            if group_name:
                distractors = vocabulary_manager.get_distractors(correct_word, 3)
                for distractor in distractors:
                    choices.append({
                        'text_en': distractor['meaning_en'],
                        'text_th': distractor['meaning_th'],
                        'is_correct': False
                    })
            else:
                # Fallback distractors
                for i in range(3):
                    choices.append({
                        'text_en': f'Incorrect meaning {i+1}',
                        'text_th': f'ความหมายที่ไม่ถูกต้อง {i+1}',
                        'is_correct': False
                    })
            
        else:
            # Level 3+: Show only English meanings
            correct_choice = {
                'text_en': correct_word['meaning_en'],
                'is_correct': True
            }
            choices.append(correct_choice)
        
        # Shuffle choices
        random.shuffle(choices)
        
        return choices
        
    except Exception as e:
        logger.error(f"Error generating choices: {e}")
        # Fallback to simple choices
        return [
            {'text_en': correct_word['meaning_en'], 'text_th': correct_word['meaning_th']},
            {'text_en': 'Incorrect meaning 1', 'text_th': 'ความหมายที่ไม่ถูกต้อง 1'},
            {'text_en': 'Incorrect meaning 2', 'text_th': 'ความหมายที่ไม่ถูกต้อง 2'},
            {'text_en': 'Incorrect meaning 3', 'text_th': 'ความหมายที่ไม่ถูกต้อง 3'}
        ]

def get_group_name_for_word(word_id):
    """Get the group name for a word"""
    try:
        word = word_manager.get_word_by_id(word_id)
        if word and 'group_id' in word:
            # In a real implementation, you would look up the group name from the group_id
            # For now, we'll return a placeholder
            return "Education & Learning"  # Placeholder
        return None
    except Exception as e:
        logger.error(f"Error getting group name for word: {e}")
        return None

def submit_answer(user_id, word_id, selected_choice_index, correct_choice_index, time_taken, session_id=None):
    """Submit an answer and update user progress"""
    try:
        # Check if answer is correct
        is_correct = (selected_choice_index == correct_choice_index)
        
        # Get current level for this word
        current_level_record =user_word_level_manager.get_user_word_level(user_id, word_id)
        current_level = current_level_record['level']
        
        # Update user's level for this word
        new_level = user_word_level_manager.update_user_word_level(user_id, word_id, is_correct)
        
        # Record progress
        if session_id:
            progress_record = user_progress_manager.record_progress(
                user_id, 
                word_id, 
                session_id, 
                current_level,  # level at time of practice
                is_correct, 
                time_taken
            )
        
        # Calculate points earned (level + 1)
        points_earned = current_level + 1 if is_correct else 0
        
        return {
            'is_correct': is_correct,
            'new_level': new_level,
            'points_earned': points_earned,
            'feedback': 'Correct!' if is_correct else 'Incorrect. Keep practicing!'
        }
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise