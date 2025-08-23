import os
import json
import logging
import random
from manager.database_manager import DatabaseManager
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VocabularyManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        self.vocab_data = self.load_vocabulary_data()
    
    def load_vocabulary_data(self):
        """Load all vocabulary data from JSON files"""
        vocab_data = []
        vocab_dir = 'vocab'
        
        if not os.path.exists(vocab_dir):
            logger.warning(f"Vocabulary directory {vocab_dir} not found")
            return vocab_data
            
        for filename in os.listdir(vocab_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(vocab_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        vocab_data.extend(data)
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
        
        return vocab_data
    
    def get_word_groups(self):
        """Get all word groups from loaded vocabulary data"""
        groups = []
        for group_data in self.vocab_data:
            if 'group_name' in group_data:
                groups.append(group_data['group_name'])
        return list(set(groups))  # Remove duplicates
    
    def get_words_in_group(self, group_name):
        """Get all words in a specific group"""
        for group_data in self.vocab_data:
            if group_data.get('group_name') == group_name:
                return group_data.get('word_list', [])
        return []
    
    def get_all_words(self):
        """Get all words from all groups"""
        all_words = []
        for group_data in self.vocab_data:
            all_words.extend(group_data.get('word_list', []))
        return all_words
    
    def get_word_by_text(self, word_text):
        """Get a word by its text"""
        all_words = self.get_all_words()
        for word in all_words:
            if word.get('word') == word_text:
                return word
        return None
    
    def get_random_word_from_group(self, group_name):
        """Get a random word from a specific group"""
        words = self.get_words_in_group(group_name)
        if words:
            return random.choice(words)
        return None
    
    def get_distractors(self, correct_word, group_name, count):
        """Get distractor words from the same group with some similarity"""
        words_in_group = self.get_words_in_group(group_name)
        
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
    def get_or_create_group(self, name):
        """Get existing group or create a new one in database"""
        try:
            conn = self.db.get_connection()
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
    
    def get_all_groups(self):
        """Get all word groups from database"""
        try:
            conn = self.db.get_connection()
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