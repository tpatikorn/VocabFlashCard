import logging
from manager.database_manager import DatabaseManager
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserProgressManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
    
    def record_progress(self, user_id, word_id, session_id, level_at_time, is_correct, time_taken):
        """Record user progress for a word"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                INSERT INTO user_progress 
                (user_id, word_id, session_id, level_at_time, is_correct, time_taken)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, word_id, session_id, level_at_time, is_correct, time_taken, attempted_at
            """, (user_id, word_id, session_id, level_at_time, is_correct, time_taken))
            
            progress = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return progress
            
        except Exception as e:
            logger.error(f"Error in record_progress: {e}")
            raise
    
    def get_user_weekly_stats(self, user_id):
        """Get user statistics for the past week"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Call the PostgreSQL function
            cur.execute("""
                SELECT * FROM get_user_weekly_stats(%s)
            """, (user_id,))
            
            stats = cur.fetchone()
            cur.close()
            conn.close()
            
            # If no stats found, return defaults
            if not stats:
                return {
                    'correct_words': 0,
                    'total_words': 0,
                    'accuracy_rate': 0.0,
                    'total_score': 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in get_user_weekly_stats: {e}")
            raise
    
    def get_user_group_performance(self, user_id):
        """Get user performance by word group"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT group_id, group_name, total_words_practiced, correct_answers, accuracy_rate, last_practiced
                FROM user_group_performance
                WHERE user_id = %s
                ORDER BY correct_answers DESC
            """, (user_id,))
            
            performance = cur.fetchall()
            cur.close()
            conn.close()
            return performance
            
        except Exception as e:
            logger.error(f"Error in get_user_group_performance: {e}")
            raise