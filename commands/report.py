
from telegram import Update
from telegram.ext import CallbackContext
import config


def report_command(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        reported_user = update.message.reply_to_message.from_user  # Rapor edilen kullanıcı
        reporter_user = update.message.from_user  # Rapor eden kişi

        # Rapor edilen kişi bilgisi admin'e bildiriliyor
        context.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,  # Admin chat ID'sine bildir
            text=(
                f"📋 Rapor edildi:\n"
                f"Kullanıcı: {reported_user.first_name} (ID: {reported_user.id})\n"
                f"Rapor Eden: {reporter_user.first_name} (ID: {reporter_user.id})"
            )
        )

        # Rapor eden kişiye bilgilendirme mesajı
        update.message.reply_text(f"📋 {reported_user.first_name} başarıyla rapor edildi.")
    else:
        update.message.reply_text("⚠️ Bir kullanıcıyı rapor etmek için bir mesaja yanıt vermeniz gerekiyor.")
