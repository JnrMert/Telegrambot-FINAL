from telegram.ext import CallbackContext
from telegram import Update
import re
from commands.db_management import increment_warning, get_warnings, blacklist_user, reset_warnings
from commands.moderation import direct_mute_user  # moderation.py'den susturma işlevini alıyoruz
import config


def is_link(message_text):
    """
    Basit bir URL kontrolü (www., http://, .com gibi)
    """
    return bool(re.search(r'(https?://|www\.)[^\s]+|\.com\b', message_text))

def detect_swear(update: Update, context: CallbackContext):
    if update.message is None or update.message.text is None:
        return

    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    username = update.message.from_user.username
    message_text = update.message.text.lower()

    if user_id in config.ADMINS:
        return  # Adminse işlem yapılmaz

    # Kötü kelimenin tek başına kullanılıp kullanılmadığını kontrol et
    for keyword in config.SPAM_KEYWORDS:
        if re.search(rf'\b{re.escape(keyword)}\b', message_text):
            try:
                # Mesajı sil
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                increment_warning(user_id)
                warnings = get_warnings(user_id)

                user_mention = f"@{username}" if username else first_name

                if warnings == 1:
                    direct_mute_user(update, context, user_id, 60)
                    context.bot.send_animation(
                        chat_id=update.effective_chat.id, 
                        animation='https://media1.tenor.com/m/Si1N3dQSEhQAAAAC/tamam-baba-sakinles.gif',
                        caption=f"⚠️ {user_mention}, bu senin {warnings}. uyarın. 1 dakika için susturuldun.❌"
                    )
                elif warnings >= 4:
                    context.bot.kick_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
                    context.bot.send_animation(
                        chat_id=update.effective_chat.id,
                        animation='https://media1.tenor.com/m/9zCgefg___cAAAAC/bane-no.gif',
                        caption=f"🚫 {user_mention}, küfür nedeniyle yasaklandın."
                    )
                    blacklist_user(user_id)
                    reset_warnings(user_id)
                else:
                    mute_durations = [300, 600, 1800]
                    direct_mute_user(update, context, user_id, mute_durations[warnings - 1])
                    context.bot.send_animation(
                        chat_id=update.effective_chat.id,
                        animation='https://media1.tenor.com/m/ycdBtRaRWU4AAAAd/nariukiyo-dj-khaled.gif',
                        caption=f"⚠️ {user_mention}, bu senin {warnings}. uyarın. {mute_durations[warnings - 1]} saniye için susturuldun.❌"
                    )
            except Exception as e:
                pass
            break

    # Link içeriyor mu kontrol et (normal üyeler için)
    if is_link(message_text):
        try:
            # Link içeren mesajı sil
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
            pass
