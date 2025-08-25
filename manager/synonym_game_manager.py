import logging
from manager.database_manager import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_random_synonym_pairs(count=2):
    """Get random pairs of synonyms from the database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # First, get the total count of synonym records
        cur.execute("SELECT COUNT(*) FROM synonyms")
        total_count = cur.fetchone()[0]
        
        if total_count < count:
            logger.warning(f"Not enough synonym records. Found {total_count}, need {count}")
            return []
        
        # Get random synonym records
        cur.execute("""
            SELECT id, category, meaning, words 
            FROM synonyms 
            ORDER BY RANDOM() 
            LIMIT %s
        """, (count,))
        
        synonym_pairs = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert to dictionary format
        result = []
        for row in synonym_pairs:
            result.append({
                'id': row[0],
                'category': row[1],
                'meaning': row[2],
                'words': row[3] if row[3] else []
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting random synonym pairs: {e}")
        return []

def start_new_game(user_id):
    """Start a new synonym game session"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert a new game record
        cur.execute("""
            INSERT INTO synonym_games (user_id)
            VALUES (%s)
            RETURNING id, user_id, played_at
        """, (user_id,))
        
        game_record = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'id': game_record[0],
            'user_id': game_record[1],
            'played_at': game_record[2]
        }
        
    except Exception as e:
        logger.error(f"Error starting new game: {e}")
        raise

def record_round_score(game_id, subgame_order, meaning, score):
    """Record the score for a round of the game"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert a new score record
        cur.execute("""
            INSERT INTO synonym_scores (game_id, subgame_order, meaning, score)
            VALUES (%s, %s, %s, %s)
            RETURNING id, game_id, subgame_order, meaning, score
        """, (game_id, subgame_order, meaning, score))
        
        score_record = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'id': score_record[0],
            'game_id': score_record[1],
            'subgame_order': score_record[2],
            'meaning': score_record[3],
            'score': score_record[4]
        }
        
    except Exception as e:
        logger.error(f"Error recording round score: {e}")
        raise

def get_game_history(user_id, limit=10):
    """Get game history for a user"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get recent games with their total scores
        cur.execute("""
            SELECT 
                sg.id,
                sg.played_at,
                COALESCE(SUM(ss.score), 0) as total_score
            FROM synonym_games sg
            LEFT JOIN synonym_scores ss ON sg.id = ss.game_id
            WHERE sg.user_id = %s
            GROUP BY sg.id, sg.played_at
            ORDER BY sg.played_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        games = cur.fetchall()
        cur.close()
        conn.close()
        
        result = []
        for game in games:
            result.append({
                'id': game[0],
                'played_at': game[1],
                'total_score': float(game[2]) if game[2] else 0.0
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting game history: {e}")
        return []

def get_game_details(game_id):
    """Get detailed information about a specific game"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get game details
        cur.execute("""
            SELECT id, user_id, played_at
            FROM synonym_games
            WHERE id = %s
        """, (game_id,))
        
        game_record = cur.fetchone()
        if not game_record:
            cur.close()
            conn.close()
            return None
        
        game = {
            'id': game_record[0],
            'user_id': game_record[1],
            'played_at': game_record[2],
            'rounds': []
        }
        
        # Get rounds for this game
        cur.execute("""
            SELECT subgame_order, meaning, score
            FROM synonym_scores
            WHERE game_id = %s
            ORDER BY subgame_order, id
        """, (game_id,))
        
        rounds = cur.fetchall()
        cur.close()
        conn.close()
        
        # Group scores by subgame_order
        round_dict = {}
        for round_record in rounds:
            subgame_order, meaning, score = round_record
            if subgame_order not in round_dict:
                round_dict[subgame_order] = {
                    'subgame_order': subgame_order,
                    'scores': []
                }
            round_dict[subgame_order]['scores'].append({
                'meaning': meaning,
                'score': float(score)
            })
        
        game['rounds'] = list(round_dict.values())
        
        return game
        
    except Exception as e:
        logger.error(f"Error getting game details: {e}")
        return None