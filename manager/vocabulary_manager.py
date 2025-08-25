import logging
import random
from manager import word_manager
from manager.database_manager import get_db_connection
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    
def get_distractors(correct_word, count):
    """Get distractor words from the same group with some similarity"""
    words_in_group = word_manager.get_words_by_group(correct_word['group_id'])
    
    # Remove the correct word from possible distractors
    distractor_candidates = [w for w in words_in_group if w.get('word') != correct_word.get('word')]
    
    # Filter by similar part of speech if available
    if correct_word.get('part_of_speech'):
        distractor_candidates = [
            w for w in distractor_candidates 
            if w.get('part_of_speech') == correct_word.get('part_of_speech')
        ]
    
    # If we don't have enough candidates, use all words in group (except correct word)
    if len(distractor_candidates) < count:
        distractor_candidates = [w for w in words_in_group if w.get('word') != correct_word.get('word')]
    
    # Randomly select the required number of distractors
    if len(distractor_candidates) >= count:
        return random.sample(distractor_candidates, count)
    elif distractor_candidates:
        # If we have fewer candidates than needed, return all of them
        return distractor_candidates
    else:
        # Fallback if no distractors found
        return []

# Database-related methods for word groups
def get_or_create_group(name):
    """Get existing group or create a new one in database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if group exists
        cur.execute("""
            SELECT id, name, created_at
            FROM word_groups 
            WHERE name = %s
        """, (name,))
        
        group = cur.fetchone()
        
        if group:
            cur.close()
            conn.close()
            return group
        else:
            # Create new group
            cur.execute("""
                INSERT INTO word_groups (name)
                VALUES (%s)
                RETURNING id, name, created_at
            """, (name,))
            
            group = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return group
            
    except Exception as e:
        logger.error(f"Error in get_or_create_group: {e}")
        raise

def get_all_groups():
    """Get all word groups from database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, name, created_at
            FROM word_groups
            ORDER BY name
        """)
        
        groups = cur.fetchall()
        cur.close()
        conn.close()
        return groups
        
    except Exception as e:
        logger.error(f"Error in get_all_groups: {e}")
        raise