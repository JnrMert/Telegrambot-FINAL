import logging
import re
from telegram import ChatPermissions, Update
from telegram.ext import CallbackContext
from datetime import timedelta
from config import SPAM_KEYWORDS, BLACKLIST, BAN_GIF_URL  # Gerekli verileri config'den alıyoruz
from commands.db_management import increment_warning, get_warnings, reset_warnings

logger = logging.getLogger(__name__)
def detect_swear(update: Update, context: CallbackContext):
    message = update.message
    if message is None:
        logger.debug("Mesaj alınmadı.")
        return

    chat_type = message.chat.type
    chat_id = message.chat_id
    user_id = message.from_user.id
    message_text = message.text.lower()

    logger.debug(f"Mesaj alındı: {message_text}, kullanıcı: {user_id}, grup: {chat_id}")

    # Yasaklı kelime kontrolü
    if any(keyword in message_text for keyword in SPAM_KEYWORDS):
        logger.debug(f"Spam kelime bulundu: {message_text}")

        try:
            context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            logger.debug(f"Mesaj silindi: {message.message_id}")

            if chat_type == 'private':
                context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ {message.from_user.first_name}, bu mesajın yasaklı kelimeler içerdiği için silindi."
                )
            elif chat_type in ['group', 'supergroup']:
                increment_warning(user_id)
                warnings = get_warnings(user_id)
                logger.info(f"Kullanıcının uyarı sayısı: {warnings}")

                if warnings == 1:
                    mute_user_for_duration(update, context, 60)
                    context.bot.send_animation(
                        chat_id=chat_id,
                        animation='https://media1.tenor.com/m/Si1N3dQSEhQAAAAC/tamam-baba-sakinles.gif',
                        caption=f"⚠️ {message.from_user.first_name}, bu senin {warnings}. uyarın. 1 dakika susturuldun."
                    )
                elif warnings >= 3:
                    context.bot.kick_chat_member(chat_id=chat_id, user_id=user_id)
                    context.bot.send_animation(
                        chat_id=chat_id,
                        animation=BAN_GIF_URL,
                        caption=f"🚫 {message.from_user.first_name}, bu senin {warnings}. uyarın ve yasaklandın."
                    )
                    reset_warnings(user_id)
                else:
                    mute_durations = [300, 600, 1800]
                    mute_user_for_duration(update, context, mute_durations[warnings - 1])
                    context.bot.send_animation(
                        chat_id=chat_id,
                        animation='https://media1.tenor.com/m/ycdBtRaRWU4AAAAd/nariukiyo-dj-khaled.gif',
                        caption=f"⚠️ {message.from_user.first_name}, bu senin {warnings}. uyarın. {mute_durations[warnings - 1]} saniye susturuldun."
                    )
        except Exception as e:
            logger.error(f"Mesaj silinirken hata: {e}")


# Kullanıcıyı susturmak için fonksiyon
def mute_user_for_duration(update: Update, context: CallbackContext, duration: int):
    user_to_mute = update.message.from_user.id
    chat_id = update.message.chat_id
    until_date = update.message.date + timedelta(seconds=duration)

    # Sadece grup mesajlarında bu işlemi yap
    if update.message.chat.type in ['group', 'supergroup']:
        context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_to_mute,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        logger.info(f"Kullanıcı {user_to_mute} {duration} saniye susturuldu.")
