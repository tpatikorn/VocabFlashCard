import logging
from datetime import date
from manager.database_manager import DatabaseManager
from manager.user_progress_manager import UserProgressManager
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserStatisticsManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        self.user_progress_manager = UserProgressManager(db_manager)
    
    def get_or_update_weekly_stats(self, user_id):
        """Get or update user statistics for the current week"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get the start of current week (Monday)
            cur.execute("SELECT DATE_TRUNC('week', CURRENT_DATE)::DATE as week_start")
            week_start = cur.fetchone()['week_start']
            
            # Try to get existing stats
            cur.execute("""
                SELECT id, user_id, week_start, words_correct, total_words_practiced, total_score, updated_at
                FROM user_statistics
                WHERE user_id = %s AND week_start = %s
            """, (user_id, week_start))
            
            stats = cur.fetchone()
            
            # If no stats exist for this week, we could create them
            # For now, we'll just return what we get from the progress table
            cur.close()
            conn.close()
            
            # Get stats from progress table
            weekly_stats = self.user_progress_manager.get_user_weekly_stats(user_id)
            
            return weekly_stats
            
        except Exception as e:
            logger.error(f"Error in get_or_update_weekly_stats: {e}")
            raise