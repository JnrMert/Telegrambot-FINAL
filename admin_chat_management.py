import logging
from telegram import ChatPermissions, Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def lock_chat(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    permissions = ChatPermissions(can_send_messages=False)
    
    try:
        context.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
        update.callback_query.message.reply_text("🔒 Chat kilitlendi.")
    except Exception as e:
        logger.error(f"Chat kilitlenirken hata oluştu: {e}")

def unlock_chat(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    permissions = ChatPermissions(can_send_messages=True)
    
    try:
        context.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
        update.callback_query.message.reply_text("🔓 Chat açıldı.")
    except Exception as e:
        logger.error(f"Chat açılırken hata oluştu: {e}")
