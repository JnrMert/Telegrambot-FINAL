import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
import config

logger = logging.getLogger(__name__)

def sites_command(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton(site['name'], url=site['url'])] for site in config.SITES]
    keyboard = InlineKeyboardMarkup(buttons)
    try:
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=config.PHOTOS['sites'],
            caption=config.CAPTIONS['sites'],
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Fotoğraf gönderilirken hata oluştu: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Bir hata oluştu, lütfen daha sonra tekrar deneyin.")

def vip_command(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton(vip['name'], url=vip['url'])] for vip in config.VIP]
    keyboard = InlineKeyboardMarkup(buttons)
    try:
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=config.PHOTOS['vips'],
            caption=config.CAPTIONS['vips'],
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"VIP fotoğrafı gönderilirken hata oluştu: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Bir hata oluştu, lütfen daha sonra tekrar deneyin.")

def bonus_command(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton(bonus['name'], url=bonus['url'])] for bonus in config.BONUSES]
    keyboard = InlineKeyboardMarkup(buttons)
    try:
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=config.PHOTOS['bonuses'],
            caption=config.CAPTIONS['bonuses'],
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Bonus fotoğrafı gönderilirken hata oluştu: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Bir hata oluştu, lütfen daha sonra tekrar deneyin.")

