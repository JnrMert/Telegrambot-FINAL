from telegram import ChatPermissions
from telegram.ext import MessageHandler, Filters, CallbackContext
from telegram import Update
import re
import time

# Kiril alfabesi (Rusça) ve Arap alfabesi için Unicode aralıkları
Cyrillic_pattern = re.compile(r'[А-Яа-яЁё]')
Arabic_pattern = re.compile(r'[\u0600-\u06FF]')

# Kullanıcıyı 15 dakika susturma fonksiyonu
def mute_user_for_foreign_language(update: Update, context: CallbackContext):
    message = update.message.text
    user = update.message.from_user
    chat_id = update.message.chat_id

    # Admin olup olmadığını kontrol et
    chat_member = context.bot.get_chat_member(chat_id=chat_id, user_id=user.id)
    if chat_member.status in ['administrator', 'creator']:
        # Eğer kullanıcı admin ise işlem yapma
        return

    # Eğer mesajda Rusça veya Arapça karakterler bulunuyorsa
    if Cyrillic_pattern.search(message) or Arabic_pattern.search(message):
        # Kullanıcıyı 15 dakika boyunca susturacak ChatPermissions
        permissions = ChatPermissions(can_send_messages=False)

        context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=permissions,
            until_date=time.time() + 90000  # 15 dakika (900 saniye)
        )

        
        # Mesajı sil
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        
    else:
        # Eğer yabancı dil değilse, bir işlem yapma
        return
