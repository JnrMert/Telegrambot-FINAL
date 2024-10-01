import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, Update
from telegram.ext import CallbackContext
import config # config.py dosyasını import ediyoruz
from config import ALLOWED_GROUPS


logger = logging.getLogger(__name__)# Üyelerin mesaj gönderme geçmişi (flood takibi için)

def track_messages(update: Update, context: CallbackContext):
    """Gelen mesajları takip eder ve son 10 mesajı saklar."""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    logger.debug(f"Mesaj alındı: {update.message.text} from user: {user_id} in chat: {chat_id}")

    if update.message and user_id != context.bot.id:  # Botun kendi mesajlarını hariç tut
        # Mesajları context üzerinden saklıyoruz
        messages = context.chat_data.get(f'recent_messages_{chat_id}', [])  
        messages.append({'message_id': update.message.message_id, 'user_id': user_id, 'timestamp': datetime.now()})

        if len(messages) > 10:
            messages.pop(0)

        context.chat_data[f'recent_messages_{chat_id}'] = messages  # Güncellenen mesaj listesini sakla
        logger.info(f"Recent messages in chat {chat_id}: {messages}")

        # Flood kontrolünü burada çağırıyoruz
        check_flooding(user_id, chat_id, context)

# Mesajları silme işlemi için grup seçimi yaptıran fonksiyon
def delete_messages(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    allowed_groups = config.ALLOWED_GROUPS

    # Eğer birden fazla allowed_group varsa grup seçimi yaptırıyoruz
    if len(allowed_groups) > 1:
        options = [[InlineKeyboardButton(f"Grup: {context.bot.get_chat(group_id).title}", callback_data=f'delete_select_group_{group_id}')] for group_id in allowed_groups]
        reply_markup = InlineKeyboardMarkup(options)
        query.message.reply_text("Hangi gruptaki mesajları silmek istiyorsunuz?", reply_markup=reply_markup)
    else:
        # Tek bir grup varsa direkt silme işlemine geçiyoruz
        delete_message_option(update, context, allowed_groups[0])

# Seçilen gruptaki mesajları silme işlemi
def delete_message_option(update: Update, context: CallbackContext, selected_group_id=None):
    query = update.callback_query
    callback_data = query.data

    # Eğer callback'den grup seçimi yapıldıysa
    if 'delete_select_group_' in callback_data:
        selected_group_id = int(callback_data.replace('delete_select_group_', ''))

    chat_id = selected_group_id if selected_group_id else update.effective_chat.id
    group_title = context.bot.get_chat(chat_id).title  # Grup adını alıyoruz
    messages = context.chat_data.get(f'recent_messages_{chat_id}', [])  # Seçilen gruptaki mesajları al

    # Eğer recent_messages boşsa, mesaj yok demektir
    if not messages:
        update.callback_query.message.reply_text(f"{group_title} için silinecek mesaj yok.")
        return
    
    # Son 5 mesajı silelim
    to_delete = messages[-5:]

    for message_id in to_delete:
        try:
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.error(f"Mesaj silinirken hata oluştu: {str(e)}")
    
    update.callback_query.message.reply_text(f"{group_title} için {len(to_delete)} mesaj silindi.")
