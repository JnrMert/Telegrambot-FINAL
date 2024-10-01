import psycopg2
import random
import json
from datetime import datetime
from config import DATABASE_URL, RAFFLE_CHAT_ID

# Veritabanı bağlantısı fonksiyonu
def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# JSON'dan çekiliş bilgilerini yükleme
def load_raffles():
    with open('raffles.json', 'r') as f:
        return json.load(f)['raffles']

# Rastgele kazananları seç
def pick_winners(raffle_id, winners_count):
    conn = get_connection()
    cur = conn.cursor()

    # Çekilişe katılan kullanıcıları seç
    cur.execute("""
    SELECT user_id
    FROM raffle_participants
    WHERE raffle_id = %s;
    """, (raffle_id,))
    
    participants = cur.fetchall()
    cur.close()
    conn.close()

    # Katılımcılardan rastgele winners_count kadar kazanan seç
    if len(participants) < winners_count:
        winners_count = len(participants)  # Yeterince katılımcı yoksa, tüm katılımcılar kazanır

    return random.sample([p[0] for p in participants], winners_count) if participants else []

# Kazananları duyurma
def announce_winners(context, raffle_id):
    raffles = load_raffles()  # JSON'dan çekilişleri yükler
    raffle = raffles[0]  # İlk çekilişi al (ID ile de seçilebilir)
    raffle_time = datetime.strptime(raffle['date'], '%Y-%m-%d %H:%M:%S')

    # Çekiliş zamanı geldiyse
    if datetime.now() >= raffle_time:
        winners = pick_winners(raffle_id, raffle['winners_count'])  # Kazananları seç

        if winners:
            winner_ids = ', '.join([str(w) for w in winners])
            context.bot.send_animation(
                chat_id=RAFFLE_CHAT_ID,  # Çekilişin duyurulacağı chat ID
                animation=raffle['gif'],
                caption=f"Tebrikler! Kazanan kullanıcılar: {winner_ids}"
            )
        else:
            context.bot.send_message(chat_id=RAFFLE_CHAT_ID, text="Çekiliş için yeterli katılımcı bulunamadı.")

# Çekilişe katılım
def join_raffle(update, context):
    user_id = update.message.from_user.id
    raffles = load_raffles()
    raffle = raffles[0]  # İlk çekilişi al

    # Kullanıcı puanlarını kontrol et
    user_points = get_user_points(user_id)
    required_points = raffle['required_points']

    if user_points < required_points:
        update.message.reply_text(f"Çekilişe katılmak için {required_points} puana ihtiyacınız var. Şu an {user_points} puanınız var.")
        return

    # Puanı düşür
    deduct_points(user_id, required_points)
    update.message.reply_text(f"Çekilişe başarıyla katıldınız! {required_points} puanınız düşürüldü.")
    
    # Kullanıcının çekilişe katılımını veritabanına ekleme
    add_participant(user_id, raffle)

# Çekilişe katılan kullanıcıyı veritabanına ekleme
def add_participant(user_id, raffle):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO raffle_participants (raffle_id, user_id)
    VALUES (%s, %s);
    """, (raffle['raffle_id'], user_id))
    conn.commit()
    cur.close()
    conn.close()
