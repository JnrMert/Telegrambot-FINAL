import logging
from threading import Thread, Timer
import time
from telegram import ChatPermissions
from config import settings

# Flood verileri için boş bir liste
data = []

# Logger oluşturma
logger = logging.getLogger(__name__)

# Mesaj silme işlevi
def del_msg(context, chat_id, msg_id):
    """
    Belirtilen mesajı silme işlevi.
    """
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        logger.info(f"Mesaj silindi: {msg_id} in chat: {chat_id}")
    except Exception as e:
        logger.error(f"Mesaj silinirken hata oluştu: {e}")

# Flood kontrol işlevi
def antiflood(context, user_id, chat_id):
    """
    Flood tespit etme ve eylemde bulunma işlevi.
    """
    counter = 0
    msg_ids = []
    
    for idx, item in enumerate(data):
        combined = f"{chat_id}:{user_id}"
        if combined in item:
            msg_id = data[idx].split(":")[2]
            msg_ids.append(int(msg_id))
            counter += 1

    # Eğer belirli bir mesaj sayısı aşıldıysa kullanıcıyı sustur
    if counter >= settings['antiflood_max_msgs']:
        # Kullanıcıyı gruptan çıkarma veya susturma işlemi
        data.clear()  # Flood verilerini temizle
        context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=time.time() + settings['timeout_duration']
        )
        logger.info(f"Kullanıcı {user_id} susturuldu. Sebep: Flooding.")

        for msg_id in msg_ids:
            Thread(target=del_msg, args=(context, chat_id, msg_id)).start()
    else:
        # Flood yapılmadıysa sadece listeyi temizle
        data.clear()

# Flood kontrol mekanizmasını başlatan fonksiyon
def on_message(update, context):
    """
    Mesaj geldiğinde flood kontrol mekanizmasını başlatan işlev.
    """
    message = update.message
    if message.chat.type == "supergroup":
        user_id = message.from_user.id
        chat_id = message.chat.id
        msg_id = message.message_id

        # Kullanıcının mesajını kaydet
        data.append(f"{chat_id}:{user_id}:{msg_id}")

        # Flood kontrolü başlat
        Timer(settings['antiflood_seconds'], antiflood, [context, str(user_id), str(chat_id)]).start()
