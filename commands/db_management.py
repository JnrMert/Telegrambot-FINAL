import psycopg2
import config
from config import DATABASE_URL

def get_connection():
    return psycopg2.connect(config.DATABASE_URL)

def increment_warning(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO warnings (user_id, count) VALUES (%s, 1) ON CONFLICT (user_id) DO UPDATE SET count = warnings.count + 1;", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_warnings(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT count FROM warnings WHERE user_id = %s;", (user_id,))
    count = cur.fetchone()
    cur.close()
    conn.close()
    return count[0] if count else 0

def blacklist_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO blacklist (user_id) VALUES (%s) ON CONFLICT DO NOTHING;", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def reset_warnings(user_id):
    """Kullanıcının uyarılarını sıfırlar."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("UPDATE warnings SET count = 0 WHERE user_id = %s;", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def reset_all_warnings():
    """Veritabanındaki tüm kullanıcıların uyarılarını sıfırlar."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE warnings SET count = 0;")
    conn.commit()
    cur.close()
    conn.close()
