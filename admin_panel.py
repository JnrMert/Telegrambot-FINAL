import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import config
from commands.db_management import reset_all_warnings

logger = logging.getLogger(__name__)

def admin_panel(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # Eğer kullanıcı admin değilse, fonksiyonu durduruyoruz
    if user_id not in config.ADMINS:
        logger.warning(f"Kullanıcı {user_id} yetkisiz erişim denemesi yaptı.")
        return

    # /admin komutunu yazan mesajı gruptan sil
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        logger.info(f"/admin komutu silindi.")
    except Exception as e:
        logger.error(f"Mesaj silinirken hata oluştu: {e}")

    # Admin panelini grupta sadece adminlerin kullanabileceği şekilde gönder
    keyboard = [
        [InlineKeyboardButton("🗑 Son 5 Mesajı Sil", callback_data='delete_messages')],
        [InlineKeyboardButton("🔒 Chat'i Kitle", callback_data='lock_chat')],
        [InlineKeyboardButton("🔓 Chat'i Aç", callback_data='unlock_chat')],
        [InlineKeyboardButton("⚠️ Uyarıları Sıfırla", callback_data='reset_warnings')],  # Yeni buton
        [InlineKeyboardButton("🚪 Çıkış", callback_data='close_admin_panel')]  # Çıkış butonu
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Admin paneli mesajını hatırlamak için mesaj ID'sini kaydediyoruz
    sent_message = context.bot.send_message(chat_id=chat_id, text="🔧 Admin Panel", reply_markup=reply_markup)
    context.chat_data['admin_panel_message_id'] = sent_message.message_id  # Mesaj ID'sini chat_data'ya kaydediyoruz


def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if user_id in config.ADMINS:
        logger.info(f"Admin buton callback çalıştırıldı. Callback data: {query.data}")

        if query.data == 'delete_messages':
            from admin_message_management import delete_messages
            delete_messages(update, context)
            _delete_bot_message(update, context)

        elif query.data == 'lock_chat':
            from admin_chat_management import lock_chat
            lock_chat(update, context)
            _delete_bot_message(update, context)

        elif query.data == 'unlock_chat':
            from admin_chat_management import unlock_chat
            unlock_chat(update, context)
            _delete_bot_message(update, context)

        elif query.data == 'reset_warnings':  # Yeni buton için fonksiyon
            from commands.db_management import reset_all_warnings
            reset_all_warnings()  # Tüm uyarıları sıfırlar
            context.bot.answer_callback_query(query.id, text="Tüm uyarılar sıfırlandı.", show_alert=True)

        elif query.data == 'close_admin_panel':
            try:
                admin_panel_message_id = context.chat_data.get('admin_panel_message_id')
                if admin_panel_message_id:
                    context.bot.delete_message(chat_id=chat_id, message_id=admin_panel_message_id)
                    logger.info("Admin paneli başarıyla silindi.")
                else:
                    logger.warning("Admin panel mesaj ID'si bulunamadı.")
            except Exception as e:
                logger.error(f"Admin panelini silerken hata oluştu: {e}")

    else:
        logger.warning(f"Kullanıcı {user_id} yetkisiz buton erişimi yaptı.")
        context.bot.answer_callback_query(query.id, text="Yetkisiz erişim.", show_alert=True)


# Botun mesajını silen yardımcı fonksiyon
def _delete_bot_message(update: Update, context: CallbackContext):
    try:
        bot_message_id = update.callback_query.message.message_id
        chat_id = update.callback_query.message.chat_id
        context.bot.delete_message(chat_id=chat_id, message_id=bot_message_id)
        logger.info("Bot mesajı başarıyla silindi.")
    except Exception as e:
        logger.error(f"Bot mesajı silinirken hata oluştu: {e}")
