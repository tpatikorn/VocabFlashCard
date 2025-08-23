import logging
from manager.database_manager import DatabaseManager
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserWordLevelManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
    
    def get_user_word_level(self, user_id, word_id):
        """Get user's current level for a word"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, user_id, word_id, level, last_practiced, created_at
                FROM user_word_levels 
                WHERE user_id = %s AND word_id = %s
            """, (user_id, word_id))
            
            level = cur.fetchone()
            cur.close()
            conn.close()
            
            # If no record exists, return default level 0
            if not level:
                return {
                    'user_id': user_id,
                    'word_id': word_id,
                    'level': 0,
                    'last_practiced': None,
                    'created_at': None
                }
            
            return level
            
        except Exception as e:
            logger.error(f"Error in get_user_word_level: {e}")
            raise
    
    def update_user_word_level(self, user_id, word_id, is_correct):
        """Update user's level for a word based on correctness"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Call the PostgreSQL function to update the level
            cur.execute("""
                SELECT update_user_word_level(%s, %s, %s)
            """, (user_id, word_id, is_correct))
            
            new_level = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            return new_level
            
        except Exception as e:
            logger.error(f"Error in update_user_word_level: {e}")
            raise
    
    def get_user_words_with_levels(self, user_id, group_id=None):
        """Get all words with user's current levels"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            if group_id:
                cur.execute("""
                    SELECT w.id as word_id, w.word, w.meaning_en, w.meaning_th,
                           w.part_of_speech, w.difficulty, w.frequency,
                           COALESCE(uwl.level, 0) as level,
                           uwl.last_practiced
                    FROM words w
                    LEFT JOIN user_word_levels uwl ON w.id = uwl.word_id AND uwl.user_id = %s
                    WHERE w.group_id = %s
                    ORDER BY w.word
                """, (user_id, group_id))
            else:
                cur.execute("""
                    SELECT w.id as word_id, w.word, w.meaning_en, w.meaning_th,
                           w.part_of_speech, w.difficulty, w.frequency,
                           COALESCE(uwl.level, 0) as level,
                           uwl.last_practiced
                    FROM words w
                    LEFT JOIN user_word_levels uwl ON w.id = uwl.word_id AND uwl.user_id = %s
                    ORDER BY w.word
                """, (user_id,))
            
            words = cur.fetchall()
            cur.close()
            conn.close()
            return words
            
        except Exception as e:
            logger.error(f"Error in get_user_words_with_levels: {e}")
            raise