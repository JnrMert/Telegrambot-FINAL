import logging
from telegram import Update , ChatPermissions
from datetime import timedelta, datetime
from telegram import Update
from telegram.ext import CallbackContext
from commands.db_management import increment_warning, get_warnings, blacklist_user, reset_warnings
import config
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG) 
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

def is_link(message_text):
    # Basit bir URL kontrolü (www., http://, .com gibi)
    return bool(re.search(r'(https?://|www\.)[^\s]+|\.com\b', message_text))

def detect_swear(update: Update, context: CallbackContext):
    if update.message is None or update.message.text is None:
        return  # Mesaj yoksa işlemi durdur

    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name  # Kullanıcının adı
    username = update.message.from_user.username  # Kullanıcının username'i
    message_text = update.message.text.lower()
    
    # Adminleri tespit etme (Admin listesine göre ayarlanmalı)
    if user_id in config.ADMINS:
        return  # Adminse işlem yapılmaz

    # Kötü kelimenin tek başına kullanılıp kullanılmadığını kontrol et
    for keyword in config.SPAM_KEYWORDS:
        if re.search(rf'\b{re.escape(keyword)}\b', message_text):
            try:
                # Mesajı sil
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

                # Uyarı sayısını artır
                increment_warning(user_id)
                warnings = get_warnings(user_id)

                user_mention = f"@{username}" if username else first_name

                if warnings == 1:
                    direct_mute_user(update, context, user_id, 60)  # 1 dakika susturma
                    context.bot.send_animation(
                        chat_id=update.effective_chat.id, 
                        animation='https://media1.tenor.com/m/Si1N3dQSEhQAAAAC/tamam-baba-sakinles.gif', 
                        caption=f"⚠️ {user_mention}, bu senin {warnings}. uyarın. Şu an 1 dakika için susturuldun.❌"
                    )
                elif warnings >= 4:
                    context.bot.kick_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
                    context.bot.send_animation(
                        chat_id=update.effective_chat.id, 
                        animation='https://media1.tenor.com/m/9zCgefg___cAAAAC/bane-no.gif', 
                        caption=f"🚫 {user_mention}, bu senin {warnings}. uyarın ve küfür nedeniyle yasaklandın."
                    )
                    blacklist_user(user_id)
                    reset_warnings(user_id)
                else:
                    mute_durations = [300, 600, 1800]
                    direct_mute_user(update, context, user_id, mute_durations[warnings - 1])
                    context.bot.send_animation(
                        chat_id=update.effective_chat.id, 
                        animation='https://media1.tenor.com/m/ycdBtRaRWU4AAAAd/nariukiyo-dj-khaled.gif', 
                        caption=f"⚠️ {user_mention}, bu senin {warnings}. uyarın. Şu an {mute_durations[warnings - 1]} saniye için susturuldun.❌"
                    )
            except Exception as e:
                logger.error(f"Mesaj işlenirken hata oluştu: {e}")
            break

    # Link içeriyor mu kontrol et (normal üyeler için)
    if is_link(message_text):
        try:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            increment_warning(user_id)
            warnings = get_warnings(user_id)

            user_mention = f"@{username}" if username else first_name
            if warnings == 1:
                direct_mute_user(update, context, user_id, 60)  # 1 dakika susturma
                context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=f"⚠️ {user_mention}, bu senin {warnings}. uyarın. Şu an 1 dakika için susturuldun.❌"
                )
            elif warnings >= 4:
                context.bot.kick_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
                context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=f"🚫 {user_mention}, bu senin {warnings}. uyarın ve link paylaşımı nedeniyle yasaklandın."
                )
                blacklist_user(user_id)
                reset_warnings(user_id)
            else:
                mute_durations = [300, 600, 1800]
                direct_mute_user(update, context, user_id, mute_durations[warnings - 1])
                context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=f"⚠️ {user_mention}, bu senin {warnings}. uyarın. Şu an {mute_durations[warnings - 1]} saniye için susturuldun.❌"
                )
        except Exception as e:
            logger.error(f"Link işlenirken hata oluştu: {e}")

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
        context.bot.send_message(chat_id=chat_id, text=f"Hata oluştu: {e}")
##############################################################################################################

def is_capslock(message_text):
    """
    Mesajın büyük harf oranını kontrol eder.
    Eğer mesajın %70'inden fazlası büyük harfse, capslock ile yazıldığı kabul edilir.
    """
    if len(message_text) < 5:  # Çok kısa mesajları göz ardı edelim
        return False
    upper_case_count = sum(1 for c in message_text if c.isupper())
    return upper_case_count / len(message_text) > 0.7

def correct_capslock(message_text):
    """
    Mesajı düzelterek büyük harfleri küçüğe çevirir, cümleleri düzgün hale getirir.
    """
    return message_text.capitalize()

def detect_capslock(update: Update, context: CallbackContext):
    logger.debug("Capslock kontrolü başlatıldı.")
    if update.message is None or update.message.text is None:
        logger.debug("Mesaj yok veya boş mesaj.")
        return  # Mesaj yoksa işlemi durdur

    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name  # Kullanıcının adı
    username = update.message.from_user.username  # Kullanıcının username'i
    message_text = update.message.text

    logger.debug(f"Gelen mesaj: {message_text}")

    # Caps lock ile yazılmış mesajları kontrol et
    if is_capslock(message_text):
        logger.debug(f"Capslock tespit edildi: {message_text}")
        try:
            # Mesajı düzelt
            corrected_message = correct_capslock(message_text)
            logger.debug(f"Düzeltilmiş mesaj: {corrected_message}")

            # Kullanıcıyı etiketlemek için username veya firstname kullanılıyor
            user_mention = f"@{username}" if username else first_name

            # Kullanıcıyı 60 saniye sustur
            direct_mute_user(update, context, user_id, 60)  # 1 dakika susturma

            # Caps lock kullanımı için uyarı mesajı, gif ve düzeltilmiş mesaj
            context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation='https://media1.tenor.com/m/4cKxc5jDVPgAAAAC/keyboard-caps-lock.gif',  # Örnek gif URL'si
                caption=f"⚠️ {user_mention}, lütfen caps lock kullanmayın! Şu an 1 dakika için susturuldun.❌"
            )

            # Düzeltilmiş mesajı tekrar gönderme
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Düzeltilmiş mesaj: {corrected_message}"
            )
        except Exception as e:
            logger.error(f"Caps lock mesajı işlenirken hata oluştu: {e}")
    else:
        logger.debug("Capslock tespit edilmedi.")

async def handle_invalid_command(update: Update, context: CallbackContext):
    await update.message.reply_text('❌ Geçersiz komut. Lütfen doğru komutu kullanın.')
