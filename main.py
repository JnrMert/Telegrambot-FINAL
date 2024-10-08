import logging
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from config import TOKEN, ADMINS, ALLOWED_GROUPS
from commands.db_management import increment_warning, get_warnings, blacklist_user, reset_warnings
from commands.moderation import mute_user, unmute_user, ban_user, handle_invalid_command
from commands.sites import sites_command, vip_command, bonus_command, site_button_command
from commands.report import report_command
from commands.yabanci import mute_user_for_foreign_language
from commands.swear_detection import detect_swear
from commands.capslock import detect_capslock
from utils.scheduler import setup_scheduler, run_sites_update, restart_bot
from utils.logging_config import setup_logging
from admin_panel import admin_panel, button_callback
from admin_chat_management import lock_chat, unlock_chat
from antiflood import on_message
from commands.sponsor_management import show_sponsor_menu, sponsor_ekle, sponsor_sil, process_sponsor_input, process_sponsor_sil


setup_logging()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def handle_custom_command(update: Update, context: CallbackContext):
    text = update.message.text
    if text.startswith('!site'):
        sites_command(update, context)
def main():
    run_sites_update()

    setup_scheduler()
    
    print("Bot çalışıyor...")

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^!sponsor$'), handle_custom_command),group=0)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_swear), group=1)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_capslock), group=2)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, mute_user_for_foreign_language),group=3)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, on_message),group=4)
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^!site$'), site_button_command), group=6)
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\d+$'), process_sponsor_sil),group=7)  # Sponsor silme adımları
    dispatcher.add_handler(MessageHandler(Filters.text, process_sponsor_input),group=8)  # Sponsor ekleme adımları
    
    dispatcher.add_handler(CommandHandler("admin", admin_panel))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    dispatcher.add_handler(CommandHandler("panel", show_sponsor_menu))  # Admin panelini açan komut
    dispatcher.add_handler(CommandHandler("sponsor_ekle", sponsor_ekle))  # Sponsor ekleme komutu
    dispatcher.add_handler(CommandHandler("sponsor_sil", sponsor_sil))  # Sponsor silme komutu
    # Kullanıcı girdilerini işleyen handler'lar
    

    dispatcher.add_handler(CommandHandler("ban", ban_user))
    dispatcher.add_handler(CommandHandler("sus", mute_user, pass_args=True))
    dispatcher.add_handler(CommandHandler("unmute", unmute_user))
    
    dispatcher.add_handler(CommandHandler("vip", vip_command))
    dispatcher.add_handler(CommandHandler("bonus", bonus_command))
    dispatcher.add_handler(CommandHandler("rapor", report_command))

    updater.start_polling()
    updater.idle()

    time.sleep(24 * 3600)
    restart_bot()

if __name__ == '__main__':
    main()
