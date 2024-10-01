import logging
from .db_management import get_connection

logger = logging.getLogger(__name__)

def update_reputation(user_id, increment=1):
    logger.info(f"Kullanıcı {user_id} için reputation güncelleniyor.")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO reputation (user_id, points) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET points = reputation.points + %s;", (user_id, increment, increment))
    conn.commit()
    cur.close()
    conn.close()

def get_reputation(user_id):
    logger.info(f"Kullanıcı {user_id} için reputation getiriliyor.")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT points FROM reputation WHERE user_id = %s;", (user_id,))
    points = cur.fetchone()
    cur.close()
    conn.close()
    return points[0] if points else 0
