
from telegram import ChatPermissions
from telegram.ext import CallbackContext
from telegram import Update
from datetime import timedelta
from commands.moderation import direct_mute_user  # moderation.py'den susturma işlevini alıyoruz


def is_capslock(message_text):
    """
    Mesajın büyük harf oranını kontrol eder.
    Eğer mesajın %70'inden fazlası büyük harfse, capslock ile yazıldığı kabul edilir.
    """
    if len(message_text) < 5:
        return False
    upper_case_count = sum(1 for c in message_text if c.isupper())
    return upper_case_count / len(message_text) > 0.7

def correct_capslock(message_text):
    """
    Mesajı düzelterek büyük harfleri küçüğe çevirir, cümleleri düzgün hale getirir.
    """
    return message_text.capitalize()

def detect_capslock(update: Update, context: CallbackContext):
    if update.message is None or update.message.text is None:
        return

    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    username = update.message.from_user.username
    message_text = update.message.text

    if is_capslock(message_text):
        try:
            corrected_message = correct_capslock(message_text)

            user_mention = f"@{username}" if username else first_name

            # Kullanıcıyı 60 saniye sustur
            direct_mute_user(update, context, user_id, 60)

            context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation='https://media1.tenor.com/m/4cKxc5jDVPgAAAAC/keyboard-caps-lock.gif',
                caption=f"⚠️ {user_mention}, lütfen caps lock kullanmayın! 1 dakika boyunca susturuldun.❌"
            )

            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Düzeltilmiş mesaj: {corrected_message}"
            )
        except Exception as e:
            pass
    else:
        return
