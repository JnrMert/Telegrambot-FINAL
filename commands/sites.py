from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
import config
import logging
from commands.sponsor_management import load_sponsor_data



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def site_button_command(update: Update, context: CallbackContext):
    sponsor_data = load_sponsor_data()  # JSON'dan sponsor verilerini yükle

    # Butonları dört sütunlu olarak ayarlıyoruz
    buttons = []
    row = []
    for sponsor in sponsor_data['sponsors']:
        row.append(InlineKeyboardButton(sponsor['name'], url=sponsor['url']))  # Butonları oluştur
        if len(row) == 3:  # Her satırda 4 buton olacak şekilde ayarlama
            buttons.append(row)
            row = []
    
    if row:  # Son satırda eksik buton kalırsa onu da ekle
        buttons.append(row)

    keyboard = InlineKeyboardMarkup(buttons)

    # Mesaj içeriği
    message = """
🎰🎰 **GÜVENİLİR SPONSOR SİTELERİMİZ** 🎰🎰

Sizler için seçtiğimiz güvenilir siteler:
"""

    # Resmin URL'sini veya Telegram dosya ID'sini ekleyin
    image_url = "https://www.papercranestore.com/image/DENEME%20BONUSU%20VEREN%20SITELER%202024.png" # URL ile resim gönderiyorsanız bu şekilde kullanabilirsiniz
    # Alternatif olarak, bir Telegram dosya ID'si kullanabilirsiniz
    # image_id = 'your-telegram-file-id'

    # Resmi ve butonları içeren mesajı gönder
    context.bot.send_photo(
        chat_id=update.message.chat_id, 
        photo=image_url,  # Buraya URL veya dosya ID'si kullanabilirsiniz
        caption=message, 
        reply_markup=keyboard, 
        parse_mode='Markdown'
    )



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
        context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Bir hata oluştu, lütfen daha sonra tekrar deneyin.")

