import logging
from telegram import Update , ChatPermissions
from datetime import timedelta, datetime
from telegram import Update
from telegram.ext import CallbackContext
from .db_management import increment_warning, get_warnings, blacklist_user
import config
from config import SPAM_KEYWORDS


def mute_user(update: Update, context: CallbackContext):
    if context.args:  # Komutla birlikte verilen argümanları kontrol et
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
            logger.error(f"Kullanıcıyı sustururken hata oluştu: {e}")
            update.message.reply_text(f'Hata: {e}')
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
            logger.error(f"Kullanıcının susturmasını kaldırırken hata oluştu: {e}")
            update.message.reply_text(f'Hata: {e}')
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
            logger.error(f"Kullanıcıyı yasaklarken hata oluştu: {e}")
    else:
        update.message.reply_text('Bir kullanıcıyı yasaklamak için bir mesaja yanıt vermeniz gerekiyor.')


def detect_swear(update: Update, context: CallbackContext):
    if update.message is None:
        return  # Mesaj yoksa işlemi durdur
    
    user_id = update.message.from_user.id
    message_text = update.message.text.lower()

    # Eğer mesaj SPAM_KEYWORDS listesindeki herhangi bir kelimeyi içeriyorsa
    if any(keyword in message_text for keyword in config.SPAM_KEYWORDS):
        try:
            # Mesajı sil
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

            # Uyarı sayısını artır
            increment_warning(user_id)
            warnings = get_warnings(user_id)

            # İlk uyarıysa kullanıcıyı 1 dakika sustur
            if warnings == 1:
                mute_user(update, context, 60)  # 1 dakika susturma
                context.bot.send_animation(
                    chat_id=update.effective_chat.id, 
                    animation='https://media1.tenor.com/m/Si1N3dQSEhQAAAAC/tamam-baba-sakinles.gif', 
                    caption=f"⚠️ {update.message.from_user.first_name}, bu senin {warnings}. uyarın. Şu an 1 dakika için susturuldun.❌"
                )
            # Eğer 5'ten fazla uyarı aldıysa kullanıcıyı yasakla
            elif warnings >= 3:
                context.bot.kick_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
                context.bot.send_animation(
                    chat_id=update.effective_chat.id, 
                    animation='https://media1.tenor.com/m/9zCgefg___cAAAAC/bane-no.gif', 
                    caption=f"🚫 {update.message.from_user.first_name}, bu senin {warnings}. uyarın ve küfür nedeniyle yasaklandın."
                )
                blacklist_user(user_id)
                reset_warnings(user_id)  # Kullanıcı yasaklandığında warning sayısını sıfırla
            # Daha fazla uyarıysa kullanıcıyı daha uzun süre sustur
            else:
                mute_durations = [300, 600, 1800]  # 5 dakika, 10 dakika, 30 dakika
                mute_user(update, context, mute_durations[warnings - 1])
                context.bot.send_animation(
                    chat_id=update.effective_chat.id, 
                    animation='https://media1.tenor.com/m/ycdBtRaRWU4AAAAd/nariukiyo-dj-khaled.gif', 
                    caption=f"⚠️ {update.message.from_user.first_name}, bu senin {warnings}. uyarın. Şu an {mute_durations[warnings - 1]} saniye için susturuldun.❌"
                )
        except Exception as e:
            logger.error(f"Mesaj işlenirken hata oluştu: {e}")


async def handle_invalid_command(update: Update, context: CallbackContext):
    await update.message.reply_text('❌ Geçersiz komut. Lütfen doğru komutu kullanın.')
