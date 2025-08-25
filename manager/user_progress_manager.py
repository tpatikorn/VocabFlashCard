import logging
from manager.database_manager import get_db_connection
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def record_progress(user_id, word_id, session_id, level_at_time, is_correct, time_taken):
    """Record user progress for a word"""
    try:
        conn = get_db_connection()
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

def get_user_weekly_stats(user_id):
    """Get user statistics for the past week"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Call the PostgreSQL function
        cur.execute("""
            SELECT * FROM get_user_weekly_stats(%s)
        """, (int(user_id),))
        
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

def get_user_group_performance(user_id):
    """Get user performance by word group"""
    try:
        conn = get_db_connection()
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
    

def get_or_update_weekly_stats(user_id):
    """Get or update user statistics for the current week"""
    try:
        conn = get_db_connection()
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
        weekly_stats = get_user_weekly_stats(user_id)
        
        return weekly_stats
        
    except Exception as e:
        logger.error(f"Error in get_or_update_weekly_stats: {e}")
        raise