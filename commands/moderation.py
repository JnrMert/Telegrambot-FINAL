from telegram import Update , ChatPermissions
from datetime import timedelta, datetime
from telegram import Update
from telegram.ext import CallbackContext
from commands.db_management import increment_warning, get_warnings, blacklist_user, reset_warnings
import config
import re

def mute_user(update: Update, context: CallbackContext, duration: int = None):
    if duration is None:  # Komutla birlikte verilen argümanları kontrol et
        if context.args:
            try:
                duration = int(context.args[0])  # İlk argümanı süre olarak kullan
            except (IndexError, ValueError):
                update.message.reply_text('Geçerli bir süre belirtin. Örnek: /sus 60')
                return
        else:
            update.message.reply_text('Bir süre belirtmelisiniz. Örnek: /sus 60')
            return
    
    if update.message.reply_to_message:
        try:
            user_to_mute = update.message.reply_to_message.from_user.id
            chat_id = update.message.chat_id
            until_date = update.message.date + timedelta(seconds=duration)

            # Kullanıcının mesaj gönderme yetkilerini kaldırıyoruz
            context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_to_mute,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            update.message.reply_text(f'🔇 Kullanıcı {duration} saniye boyunca susturuldu.')
        except Exception as e:
            pass
    else:
        update.message.reply_text('Bir kullanıcıyı susturmak için bir mesaja yanıt vermeniz gerekiyor.')


def unmute_user(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id not in config.ADMINS:  # Admin kontrolü
        update.message.reply_text('⚠️ Bu komutu yalnızca adminler kullanabilir.')
        return
    
    if update.message.reply_to_message:
        try:
            user_to_unmute = update.message.reply_to_message.from_user.id
            chat_id = update.message.chat_id

            # Kullanıcının tüm yetkilerini geri veriyoruz
            context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_to_unmute,
                permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True)
            )
            update.message.reply_text('🔊 Kullanıcının susturması kaldırıldı.')
        except Exception as e:
            pass
    else:
        update.message.reply_text('Bir kullanıcının susturmasını kaldırmak için bir mesaja yanıt vermeniz gerekiyor.')

# Kullanıcıyı yasaklama fonksiyonu (Sadece adminler)
def ban_user(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id not in config.ADMINS:  # Admin kontrolü
        update.message.reply_text('⚠️ Bu komutu yalnızca adminler kullanabilir.')
        return
    
    if update.message.reply_to_message:
        try:
            user_to_ban = update.message.reply_to_message.from_user.id
            chat_id = update.message.chat_id

            context.bot.kick_chat_member(chat_id=chat_id, user_id=user_to_ban)
            update.message.reply_text(f'🚫 Kullanıcı başarıyla yasaklandı: {update.message.reply_to_message.from_user.username}')
        except Exception as e:
            pass
    else:
        update.message.reply_text('Bir kullanıcıyı yasaklamak için bir mesaja yanıt vermeniz gerekiyor.')

def direct_mute_user(update: Update, context: CallbackContext, user_id: int, duration: int):

    chat_id = update.effective_chat.id
    until_date = update.message.date + timedelta(seconds=duration)

    try:
        context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
    except Exception as e:
        pass
##############################################################################################################

async def handle_invalid_command(update: Update, context: CallbackContext):
    await update.message.reply_text('❌ Geçersiz komut. Lütfen doğru komutu kullanın.')
