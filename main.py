import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from config import TOKEN, ADMINS, ALLOWED_GROUPS
from commands.db_management import increment_warning, get_warnings, blacklist_user, reset_warnings
from commands.moderation import mute_user, unmute_user, ban_user, detect_swear, handle_invalid_command
from commands.sites import sites_command, vip_command, bonus_command
from commands.report import report_command
from commands.reputation import get_reputation, update_reputation
from raffles import join_raffle
from utils.scheduler import setup_scheduler
from utils.logging_config import setup_logging
from admin_panel import admin_panel, button_callback
from admin_message_management import track_messages, delete_messages, delete_message_option
from admin_chat_management import lock_chat, unlock_chat
from antiflood import on_message

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Logging ayarları
setup_logging()

def main():
    # Updater ve Dispatcher ayarları
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Komut işleyicileri
    dispatcher.add_handler(CommandHandler("admin", admin_panel))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    
    # Moderasyon komutları
    dispatcher.add_handler(CommandHandler("ban", ban_user))
    dispatcher.add_handler(CommandHandler("sus", mute_user, pass_args=True))
    dispatcher.add_handler(CommandHandler("unmute", unmute_user))
    
    # Site komutları
    dispatcher.add_handler(CommandHandler("siteler", sites_command))
    dispatcher.add_handler(CommandHandler("vip", vip_command))
    dispatcher.add_handler(CommandHandler("bonus", bonus_command))

    # Raporlama komutları
    dispatcher.add_handler(CommandHandler("report", report_command))
    dispatcher.add_handler(CommandHandler("cekilis", join_raffle))

#  Flood kontrol işlevini ekleyin
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.chat_type.groups, on_message))
    # Mesaj işleme ve küfür tespiti
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_swear))
    # Mesaj takibi
    dispatcher.add_handler(MessageHandler(Filters.chat_type.groups & Filters.text & ~Filters.command, track_messages))
    dispatcher.add_handler(MessageHandler(Filters.chat_type.groups & Filters.text, delete_messages))
    dispatcher.add_handler(MessageHandler(Filters.chat_type.groups & Filters.command, delete_message_option))
    



    # Zamanlayıcıyı başlat
    setup_scheduler()

    # Botu başlat
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
