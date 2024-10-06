import json
import os
from telegram import Update
from telegram.ext import CallbackContext
from config import ADMINS

# JSON dosyasını yükleme fonksiyonu
def load_sponsor_data():
    script_dir = os.path.dirname(__file__)  # Betiğin bulunduğu dizin
    file_path = os.path.join(script_dir, 'sponsors.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# JSON dosyasına veri yazma fonksiyonu
def save_sponsor_data(data):
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'sponsors.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Admin kontrol fonksiyonu
def is_admin(user_id):
    return user_id in ADMINS

# Admin panelini gösterme fonksiyonu
def show_sponsor_menu(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Admin kontrolü
    if not is_admin(user_id):
        update.message.reply_text("Bu işlemi sadece adminler gerçekleştirebilir.")
        return

    # Özel mesaj kontrolü
    if update.message.chat.type != "private":
        update.message.reply_text("Bu işlemi yalnızca özel mesajda gerçekleştirebilirsiniz.")
        return

    message = """
    Admin Paneli:
    1. Sponsor eklemek için: /sponsor_ekle
    2. Sponsor silmek için: /sponsor_sil
    3. Admin panelini kapatmak için: /panel_kapat
    """
    
    update.message.reply_text(message)

# Sponsor ekleme fonksiyonu
def sponsor_ekle(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Admin kontrolü
    if not is_admin(user_id):
        update.message.reply_text("Bu işlemi sadece adminler gerçekleştirebilir.")
        return

    # Özel mesaj kontrolü
    if update.message.chat.type != "private":
        update.message.reply_text("Bu işlemi yalnızca özel mesajda gerçekleştirebilirsiniz.")
        return

    update.message.reply_text("Lütfen eklemek istediğiniz sponsorun adını girin:")
    context.user_data['add_sponsor_step'] = 'name'

# Sponsor ekleme adımları
def process_sponsor_input(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Admin kontrolü
    if not is_admin(user_id):
        update.message.reply_text("Bu işlemi sadece adminler gerçekleştirebilir.")
        return

    # Özel mesaj kontrolü
    if update.message.chat.type != "private":
        update.message.reply_text("Bu işlemi yalnızca özel mesajda gerçekleştirebilirsiniz.")
        return

    if context.user_data.get('add_sponsor_step') == 'name':
        context.user_data['new_sponsor_name'] = update.message.text
        update.message.reply_text("Lütfen sponsorun URL'sini girin:")
        context.user_data['add_sponsor_step'] = 'url'
    elif context.user_data.get('add_sponsor_step') == 'url':
        url = update.message.text
        name = context.user_data['new_sponsor_name']

        sponsor_data = load_sponsor_data()
        sponsor_data['sponsors'].append({'name': name, 'url': url})
        save_sponsor_data(sponsor_data)

        update.message.reply_text(f"{name} başarıyla eklendi!")
        context.user_data.pop('add_sponsor_step')

# Sponsor silme fonksiyonu
def sponsor_sil(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Admin kontrolü
    if not is_admin(user_id):
        update.message.reply_text("Bu işlemi sadece adminler gerçekleştirebilir.")
        return

    # Özel mesaj kontrolü
    if update.message.chat.type != "private":
        update.message.reply_text("Bu işlemi yalnızca özel mesajda gerçekleştirebilirsiniz.")
        return

    sponsor_data = load_sponsor_data()
    if not sponsor_data['sponsors']:
        update.message.reply_text("Silinecek sponsor bulunamadı.")
        return
    
    sponsor_list = "\n".join([f"{i+1}. {sponsor['name']}" for i, sponsor in enumerate(sponsor_data['sponsors'])])
    update.message.reply_text(f"Silmek istediğiniz sponsorun numarasını seçin:\n{sponsor_list}")
    context.user_data['delete_sponsor_step'] = 'choose'

# Sponsor silme adımları
def process_sponsor_sil(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Admin kontrolü
    if not is_admin(user_id):
        update.message.reply_text("Bu işlemi sadece adminler gerçekleştirebilir.")
        return

    # Özel mesaj kontrolü
    if update.message.chat.type != "private":
        update.message.reply_text("Bu işlemi yalnızca özel mesajda gerçekleştirebilirsiniz.")
        return

    if context.user_data.get('delete_sponsor_step') == 'choose':
        try:
            sponsor_index = int(update.message.text) - 1
            sponsor_data = load_sponsor_data()

            if 0 <= sponsor_index < len(sponsor_data['sponsors']):
                sponsor_name = sponsor_data['sponsors'][sponsor_index]['name']
                del sponsor_data['sponsors'][sponsor_index]
                save_sponsor_data(sponsor_data)
                update.message.reply_text(f"{sponsor_name} başarıyla silindi!")
                context.user_data.pop('delete_sponsor_step')
            else:
                update.message.reply_text("Geçersiz numara, lütfen geçerli bir numara girin.")
        except ValueError:
            update.message.reply_text("Lütfen geçerli bir numara girin.")
