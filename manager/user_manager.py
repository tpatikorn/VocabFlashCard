import logging
from manager.database_manager import get_db_connection
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_or_create_user(google_id, email, given_name, family_name, name, picture_url):
    """Get existing user or create a new one"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user exists
        cur.execute("""
            SELECT id, google_id, email, given_name, family_name, name, picture_url, created_at, last_login
            FROM users 
            WHERE google_id = %s
        """, (google_id,))
        
        user = cur.fetchone()
        
        if user:
            # Update last login
            cur.execute("""
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE google_id = %s
            """, (google_id,))
            conn.commit()
            cur.close()
            conn.close()
            return user
        else:
            # Create new user
            # Parse name into given_name and family_name if needed
            if ' ' in name:
                given_name, family_name = name.rsplit(' ', 1)
            else:
                given_name, family_name = name, ''
                
            cur.execute("""
                INSERT INTO users (google_id, email, name, given_name, family_name, picture_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, google_id, email, name, given_name, family_name, picture_url, created_at, last_login
            """, (google_id, email, name, given_name, family_name, picture_url))
            
            user = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return user
            
    except Exception as e:
        logger.error(f"Error in get_or_create_user: {e}")
        raise

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, google_id, email, name, given_name, family_name, picture_url, created_at, last_login
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
        
    except Exception as e:
        logger.error(f"Error in get_user_by_id: {e}")
        raise