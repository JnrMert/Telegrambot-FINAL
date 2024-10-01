import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import threading
import time
import config

# Logging ayarları
logger = logging.getLogger(__name__)

TOKEN = config.TOKEN
bot = Bot(TOKEN)

# Otomatik mesaj gönderme fonksiyonu
def send_auto_message(message_data):
    buttons = [[InlineKeyboardButton(button['text'], url=button['url'])] for button in message_data['buttons']]

    # Mesajı sadece botun bulunduğu gruplara gönder
    for group_id in config.ALLOWED_GROUPS:
        try:
            # Mesajda 'photo' veya 'gif' kontrolü yapalım
            if 'photo' in message_data:
                bot.send_photo(chat_id=group_id, photo=message_data['photo'], caption=message_data['message'], reply_markup=InlineKeyboardMarkup(buttons))
                logger.info(f"Fotoğraf {group_id} grubuna başarıyla gönderildi.")
            elif 'gif' in message_data:
                bot.send_animation(chat_id=group_id, animation=message_data['gif'], caption=message_data['message'], reply_markup=InlineKeyboardMarkup(buttons))
                logger.info(f"GIF {group_id} grubuna başarıyla gönderildi.")
            else:
                bot.send_message(chat_id=group_id, text=message_data['message'], reply_markup=InlineKeyboardMarkup(buttons))
                logger.info(f"Mesaj {group_id} grubuna başarıyla gönderildi.")
        except Exception as e:
            logger.error(f"Mesaj {group_id} grubuna gönderilemedi: {str(e)}")

# Otomatik mesaj gönderme işlemini zamanlayıcıyla tetikleme
def schedule_auto_message(interval_minutes, message_data):
    while True:
        time.sleep(interval_minutes * 60)
        send_auto_message(message_data)

# Tüm mesajları zamanlayıcıya ekleyen fonksiyon
def setup_auto_message_scheduler():
    for message in config.AUTOMESSAGES:
        interval_minutes = message['interval_minutes']
        message_data = message
        threading.Thread(target=schedule_auto_message, args=(interval_minutes, message_data)).start()
        logger.info(f"Otomatik mesaj zamanlandı: {message['message']} her {interval_minutes} dakikada bir gönderilecek.")
