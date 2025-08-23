import logging
from manager.database_manager import DatabaseManager
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
    
    def add_word(self, group_id, word, part_of_speech, meaning_en, meaning_th, 
                 examples=None, synonyms=None, antonyms=None, word_forms=None, 
                 difficulty=None, frequency=None):
        """Add a new word to the database"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                INSERT INTO words 
                (group_id, word, part_of_speech, meaning_en, meaning_th, examples, 
                 synonyms, antonyms, word_forms, difficulty, frequency)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, group_id, word, part_of_speech, meaning_en, meaning_th,
                         examples, synonyms, antonyms, word_forms, difficulty, frequency,
                         created_at
            """, (group_id, word, part_of_speech, meaning_en, meaning_th,
                  examples or [], synonyms or [], antonyms or [], word_forms or [],
                  difficulty, frequency))
            
            word_record = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return word_record
            
        except Exception as e:
            logger.error(f"Error in add_word: {e}")
            raise
    
    def get_word_by_id(self, word_id):
        """Get word by ID"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, group_id, word, part_of_speech, meaning_en, meaning_th,
                       examples, synonyms, antonyms, word_forms, difficulty, frequency,
                       created_at
                FROM words 
                WHERE id = %s
            """, (word_id,))
            
            word = cur.fetchone()
            cur.close()
            conn.close()
            return word
            
        except Exception as e:
            logger.error(f"Error in get_word_by_id: {e}")
            raise
    
    def get_words_by_group(self, group_id):
        """Get all words in a group"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, group_id, word, part_of_speech, meaning_en, meaning_th,
                       examples, synonyms, antonyms, word_forms, difficulty, frequency,
                       created_at
                FROM words 
                WHERE group_id = %s
                ORDER BY word
            """, (group_id,))
            
            words = cur.fetchall()
            cur.close()
            conn.close()
            return words
            
        except Exception as e:
            logger.error(f"Error in get_words_by_group: {e}")
            raise
    
    def get_words_by_level_and_group(self, level, group_id, limit=None):
        """Get words at a specific level within a group"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT w.id, w.group_id, w.word, w.part_of_speech, w.meaning_en, w.meaning_th,
                       w.examples, w.synonyms, w.antonyms, w.word_forms, w.difficulty, w.frequency,
                       w.created_at
                FROM words w
                JOIN user_word_levels uwl ON w.id = uwl.word_id
                WHERE uwl.level = %s AND w.group_id = %s
                ORDER BY w.word
            """
            
            params = [level, group_id]
            
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            cur.execute(query, params)
            
            words = cur.fetchall()
            cur.close()
            conn.close()
            return words
            
        except Exception as e:
            logger.error(f"Error in get_words_by_level_and_group: {e}")
            raise