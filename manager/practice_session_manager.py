import logging
from manager.database_manager import get_db_connection
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_session(user_id):
    """Create a new practice session"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO practice_sessions (user_id)
            VALUES (%s)
            RETURNING id, user_id, start_time, end_time, total_score, words_attempted, words_correct
        """, (user_id,))
        
        session = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return session
        
    except Exception as e:
        logger.error(f"Error in create_session: {e}")
        raise

def end_session(session_id, total_score, words_attempted, words_correct):
    """End a practice session"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            UPDATE practice_sessions
            SET end_time = CURRENT_TIMESTAMP,
                total_score = %s,
                words_attempted = %s,
                words_correct = %s
            WHERE id = %s
            RETURNING id, user_id, start_time, end_time, total_score, words_attempted, words_correct
        """, (total_score, words_attempted, words_correct, session_id))
        
        session = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return session
        
    except Exception as e:
        logger.error(f"Error in end_session: {e}")
        raise

def get_user_sessions(user_id, limit=10):
    """Get recent practice sessions for a user"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, user_id, start_time, end_time, total_score, words_attempted, words_correct
            FROM practice_sessions
            WHERE user_id = %s
            ORDER BY start_time DESC
            LIMIT %s
        """, (user_id, limit))
        
        sessions = cur.fetchall()
        cur.close()
        conn.close()
        return sessions
        
    except Exception as e:
        logger.error(f"Error in get_user_sessions: {e}")
        raise